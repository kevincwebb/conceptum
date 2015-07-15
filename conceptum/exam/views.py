import datetime
import operator

from django import forms
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext, loader
from django.views import generic
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.exceptions import PermissionDenied
from django.db import transaction

import reversion
from braces.views import LoginRequiredMixin, UserPassesTestMixin, StaffuserRequiredMixin

from profiles.mixins import ContribRequiredMixin, StaffRequiredMixin
from interviews.models import get_concept_list, DummyConcept as Concept #TEMPORARY: DummyConcept
from interviews.models import Excerpt #not temporary
from .models import Exam, ResponseSet, ExamResponse, QuestionResponse, FreeResponseQuestion,\
                    MultipleChoiceQuestion, MultipleChoiceOption, FreeResponseResponse,\
                    MultipleChoiceResponse, ExamKind, ExamStage, Question
from .forms import SelectConceptForm, AddFreeResponseForm, AddMultipleChoiceForm, \
                   NewResponseSetForm, DistributeForm, ExamResponseForm, CleanupForm, \
                   MultipleChoiceEditForm, FreeResponseVersionForm, MultipleChoiceVersionForm, \
                   FinalizeSelectForm, FinalizeOrderForm, FinalizeConfirmForm
from .mixins import DevelopmentMixin, DistributionMixin, CurrentAppMixin


def get_data(exam):
    mc = {}
    fr = {}
    for concept in get_concept_list():
        concept_type = ContentType.objects.get_for_model(concept)
        fr_question_list = FreeResponseQuestion.objects.filter(exam = exam,
                                                               content_type__pk=concept_type.id,
                                                               object_id=concept.id)
        mc_question_list = MultipleChoiceQuestion.objects.filter(exam = exam,
                                                               content_type__pk=concept_type.id,
                                                               object_id=concept.id)
        fr[concept] = fr_question_list
        mc[concept] = mc_question_list
    return [fr, mc]


    
####################### Index and Detail Pages ###########################################

class ExamDevIndexView(LoginRequiredMixin,
                       ContribRequiredMixin,
                       CurrentAppMixin,
                       generic.ListView):
    """
    Landing page for exam development. This page will list all surveys or CI exams that
    are in the Development stage.
    
    Only staff users have the ability to create new Surveys and Exams.
    """
    model = Exam
    
    def get_template_names(self, *args, **kwargs):
        if (not Exam.objects.filter(kind=self.exam_kind, stage=ExamStage.DEV)):
            return 'exam/index_dev_empty.html'
        else:
            return 'exam/index_dev.html'
    
    def can_create_new(self):
        if self.request.user.is_staff:
            if self.exam_kind == ExamKind.SURVEY:
                return True
            if not Exam.objects.filter(kind=ExamKind.CI).exclude(stage=ExamStage.CLOSED):
                return True
        return False
       
    def get_context_data(self,**kwargs):
        context = super(ExamDevIndexView, self).get_context_data(**kwargs)
        
        ex_list = Exam.objects.filter(kind=self.exam_kind, stage=ExamStage.DEV)
        #format: [[exam, stat, list, goes, here...], [exam, stats, go, here], ...]
        exams = []
        for ex in ex_list:
            qset = ex.question_set.all()
            exam_item = [ex]
            qs = "Questions: " + len(qset).__str__()
            concepts = []
            for q in qset:
                concept = q.content_object.name
                if (concept not in concepts and len(concepts) <= 5):
                    concepts.append(q.content_object.name)
                elif(len(concepts) == 5):
                    concepts.append("...")
                    break;
            concepts = ", ".join(concepts)
            concepts = "Concepts: " + concepts
            exam_item = [ex, [qs, concepts]]
            exams.append(exam_item)
            
        context['exams'] = exams
        context['can_create_new'] = self.can_create_new()
        return context


class ExamDistIndexView(LoginRequiredMixin,
                        CurrentAppMixin,
                        generic.ListView):
    """
    Landing page for exam distribution. This page will list all surveys or CI exams that
    are in the Distribution stage.
    """
    model = Exam
    template_name = 'exam/index_dist.html'
    
    def make_exam_list(self, ex_list):
        """
        format: [[exam, stat, list, goes, here...], [exam, stats, go, here], ...]
        """
        exams = []
        for ex in ex_list:
            qset = ex.multiplechoicequestion_set.all()
            exam_item = [ex]
            qs = "Questions: " + len(qset).__str__()
            concepts = []
            for q in qset:
                concept = q.content_object.name
                if ( len(concepts) <= 5 and concept not in concepts):
                    concepts.append(q.content_object.name)
                elif(len(concepts) == 5):
                    concepts.append("...")
                    break;
            concepts = ", ".join(concepts)
            concepts = "Concepts: " + concepts
            
            rsets = ex.responseset_set.all()
            ##TODO##
            avgscore = "Average Score: ##"
            ####
            numResponses = 0
            for rset in rsets:
                numResponses += len(rset.examresponse_set.all())
                
            responses = "Responses: " + numResponses.__str__()
            timesDistributed = "Times Distributed: " + len(rsets).__str__()
            exid = "Exam Id: " + ex.id.__str__()
            exam_item = [ex, [qs, responses, exid, avgscore, timesDistributed, concepts]]
            exams.append(exam_item)
        return exams
       
    def get_context_data(self,**kwargs):
        context = super(ExamDistIndexView, self).get_context_data(**kwargs)
        ex_list = Exam.objects.filter(kind=self.exam_kind, stage=ExamStage.DIST)   
        context['distributable'] = self.make_exam_list(
            Exam.objects.filter(kind=self.exam_kind, stage=ExamStage.DIST))
        context['closed'] = self.make_exam_list(
            Exam.objects.filter(kind=self.exam_kind, stage=ExamStage.CLOSED))
        return context


class ExamDetailView(LoginRequiredMixin,
                     ContribRequiredMixin,
                     CurrentAppMixin,
                     generic.DetailView):
    """
    View exam details and questions.
    """
    model = Exam
    pk_url_kwarg = 'exam_id'
    
    
    def get_data(self, **kwargs):
        """
        Returns 2 dictionaries (in a tuple), each dict maps each concept to a list of
        all associated questions of that question type.
        """
        mc = {}
        fr = {}
        for concept in get_concept_list():
            concept_type = ContentType.objects.get_for_model(concept)
            fr[concept] = FreeResponseQuestion.objects.filter(exam = self.object,
                                                              content_type__pk=concept_type.id,
                                                              object_id=concept.id)
            mc_qSet= MultipleChoiceQuestion.objects.filter(exam = self.object,
                                                                content_type__pk=concept_type.id,
                                                                object_id=concept.id)
            mc_list = []
            for q in mc_qSet:
                mc_list.append([q, q.multiplechoiceoption_set.all()])
            mc[concept] = mc_list
        return (fr, mc)
    
    def get_context_data(self, **kwargs):
        context = super(ExamDetailView, self).get_context_data(**kwargs)
        data = self.get_data()
        context['freeresponsequestion_list']=data[0]
        context['multiplechoicequestion_list']=data[1]
        context['exam'] = self.object
        return context


class DevDetailView(DevelopmentMixin,
                    ExamDetailView):
    template_name = 'exam/development_detail.html'
    
    
class DistDetailView(DistributionMixin,
                     ExamDetailView):
    template_name = 'exam/distribute_detail.html'



######################### Create, Copy, Delete, etc. Exams ##############################

class ExamCreateView(LoginRequiredMixin,
                     StaffRequiredMixin,
                     CurrentAppMixin,
                     generic.CreateView):
    """
    CreateView to create a survey/exam.
    
    We may want to make this happen automatically as follows:
        - working survey is created automatically
        - once approved by staff user, frozen version can be sent out
        - working survey could continue to be improved, and new frozen versions made
        - the same process would go for exams, once that stage is activated
    """
    model = Exam
    template_name = 'exam/new_exam.html'
    form_class =  forms.models.modelform_factory(Exam,
                                                 fields=('name','description','randomize'),
                                                 widgets={"description": forms.Textarea })

    def form_valid(self, form):
        form.instance.kind = self.exam_kind
        return super(ExamCreateView,self).form_valid(form)

    def get_success_url(self):
        return reverse('exam:index', current_app=self.current_app)
    

class ExamEditView(LoginRequiredMixin,
                   StaffRequiredMixin,
                   CurrentAppMixin,
                   generic.UpdateView):
    """
    UpdateView to edit a survey/exam.
    """
    model = Exam
    pk_url_kwarg = 'exam_id'
    template_name = 'exam/edit_exam.html'
    form_class =  forms.models.modelform_factory(Exam,
                                                 fields=('name','description','randomize'),
                                                 widgets={"description": forms.Textarea })

    def form_valid(self, form):
        return super(ExamEditView,self).form_valid(form)

    def get_success_url(self):
        return reverse('exam:detail', args=[self.object.id], current_app=self.current_app)


class ExamCopyView(LoginRequiredMixin,
                   StaffRequiredMixin,
                   CurrentAppMixin,
                   generic.UpdateView):
    """
    Make a new exam that looks like this one. Original exam must be in the distribution
    or closed stage.
    
    Copies all questions and options. Because they are new objects, they begin with clean
    version histories (versions only point to old objects, and are not copied).
    
    With surveys, any distributable survey may be copied at any time. With CIs, we try to keep
    only 1 CI in development at any time, so copying is only allowed if there are no CIs in
    development.
    """
    template_name = 'exam/copy_exam.html'
    model = Exam
    pk_url_kwarg = 'exam_id'
    form_class =  forms.models.modelform_factory(Exam,
                                                 fields=('name','description','randomize'),
                                                 widgets={"description": forms.Textarea })
    
    def dispatch(self, request, *args, **kwargs):
        """
        PermissionDenied if exam.kind does not match current app, or if the app
        isn't in the Distribute or Closed stage.
        
        Redirect if we are looking at a CI and there is already another CI in the
        Development stage.
        """
        self.set_current_app(request)
        exam = get_object_or_404(Exam, pk=self.kwargs['exam_id'])
        if (exam.kind != self.exam_kind
            or exam.can_develop()):
                raise PermissionDenied
        if (exam.kind == ExamKind.CI
            and Exam.objects.filter(kind=ExamKind.CI, stage=ExamStage.DEV)):
                return HttpResponseRedirect(
                    reverse('exam:copy_denied', args=[exam.id], current_app=self.current_app))
        return super(ExamCopyView, self).dispatch(request, *args, **kwargs)
    
    def get_initial(self):
        return {'name':'%s (copy)' % self.object.name,
                'description':'%s\n\n[copied from %s]' % (self.object.description, self.object.name)}

    def form_valid(self, form):
        new_exam = Exam.objects.create(name = form.cleaned_data.get('name'),
                                       description = form.cleaned_data.get('description'),
                                       randomize = form.cleaned_data.get('randomize'),
                                       kind = self.exam_kind)
        for question in self.object.freeresponsequestion_set.all():
            with transaction.atomic(), reversion.create_revision():
                question.pk = None
                question.exam = new_exam
                question.save()
        for question in self.object.multiplechoicequestion_set.all():
            with transaction.atomic(), reversion.create_revision():
                old_pk = question.pk
                question.pk = None
                question.exam = new_exam
                question.save()
                old_question = MultipleChoiceQuestion.objects.get(pk=old_pk)
                for option in old_question.multiplechoiceoption_set.all():
                    option.pk = None
                    option.question = question
                    option.save()
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse('exam:index', current_app=self.current_app)


class CopyDeniedView(LoginRequiredMixin,
                     StaffRequiredMixin,
                     generic.DetailView):
    model = Exam
    pk_url_kwarg = 'exam_id'
    template_name = 'exam/copy_denied.html'


class ExamDeleteView(LoginRequiredMixin,
                     StaffRequiredMixin,
                     DevelopmentMixin,
                     CurrentAppMixin,
                     generic.DeleteView):
    """    
    Deletes an Exam, all Questions, and also deletes all related revisions
    (deleted question can't be recovered).
    """
    model = Exam
    pk_url_kwarg = 'exam_id'
    template_name = 'exam/delete_exam.html'
    
    def delete(self, request, *args, **kwargs):
        for question in self.get_object().question_set.all():
            versions = reversion.get_for_object(question)
            for version in versions:
                version.revision.delete()
        self.get_object().delete()
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse('exam:index', current_app=self.current_app)
    

class ExamCloseView(LoginRequiredMixin,
                    StaffRequiredMixin,
                    DistributionMixin,
                    CurrentAppMixin,
                    generic.DeleteView):
    """    
    Closes an Exam so that it cannot be distributed.
    
    Using DeleteView was convenient, but this view does not actually delete an objects.
    """
    model = Exam
    pk_url_kwarg = 'exam_id'
    template_name = 'exam/close_exam.html'
    
    def delete(self, request, *args, **kwargs):
        exam = self.get_object()
        exam.stage = ExamStage.CLOSED
        exam.save()
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse('exam:distribute_index', current_app=self.current_app)



############################# DEVELOPMENT ############################################

class SelectConceptView(LoginRequiredMixin,
                        ContribRequiredMixin,
                        DevelopmentMixin,
                        CurrentAppMixin,
                        generic.FormView):
    """
    Lists all Concepts in the database, Select a concept to add a question
    about that concept
    """
    template_name = 'exam/select.html'
    form_class = SelectConceptForm
    
    def get_context_data(self, **kwargs):
        context = super(SelectConceptView, self).get_context_data(**kwargs)
        context['exam'] = self.exam
        return context
 
    def form_valid(self, form):
        concept = form.cleaned_data.get('concept')
        return HttpResponseRedirect(reverse('exam:question_create', current_app=self.current_app,
            kwargs ={'exam_id':self.exam.id,'concept_id':concept.id,'question_type':'fr' }))


class QuestionCreateView(LoginRequiredMixin,
                         ContribRequiredMixin,
                         DevelopmentMixin,
                         CurrentAppMixin,
                         generic.FormView):
    """
    FormView to add a new question
    """
    
    template_name = 'exam/question_create.html'

    # make sure our url arguments are good
    def dispatch(self, *args, **kwargs):
        self.concept = get_object_or_404(Concept, pk=self.kwargs['concept_id'])
        self.question_type = self.kwargs['question_type']
        if (self.question_type != 'fr' and self.question_type != 'mc'):
            raise Http404
        return super(QuestionCreateView, self).dispatch(*args, **kwargs)

    # different form depending on type of question
    def get_form_class(self):
        if(self.question_type == 'fr'):
            return AddFreeResponseForm
        if(self.question_type == 'mc'):
            return AddMultipleChoiceForm
    
    def get_context_data(self,**kwargs):
        context = super(QuestionCreateView, self).get_context_data(**kwargs)
        concept_type = ContentType.objects.get_for_model(Concept)
        
        if(self.question_type == 'mc'):
            context['question_type'] = 'multiple_choice'   
        elif(self.question_type == 'fr'):
            context['question_type'] = 'free_response'
        
        context['exam'] = self.exam
        context['concept'] = self.concept
        context['excerpt_list']=Excerpt.objects.filter(content_type__pk=concept_type.id,
                                                       object_id=self.concept.id)
        return context
    
    def get_success_url(self):
        return reverse('exam:detail', args=[self.exam.id], current_app=self.current_app)
    
    @transaction.atomic()
    @reversion.create_revision()
    def form_valid(self, form):
        concept_type = ContentType.objects.get_for_model(Concept)
        # we could move the object creation to each form's save() method, however,
        # we would need to pass self.exam and self.concept to the form
        if (self.question_type == 'fr'):
            FreeResponseQuestion.objects.create(exam = self.exam,
                                                question = form.cleaned_data.get('question'),
                                                image = form.cleaned_data.get('image'),
                                                content_type = concept_type,
                                                object_id = self.concept.id)
        if (self.question_type == 'mc'):
            q = MultipleChoiceQuestion.objects.create(exam = self.exam,
                                                      question = form.cleaned_data.get('question'),
                                                      image = form.cleaned_data.get('image'),
                                                      content_type = concept_type,
                                                      object_id = self.concept.id)
            x=1
            choice_text = form.cleaned_data.get("choice_%d" % x)
            while (choice_text):
                correct = False
                if int(form.cleaned_data.get("correct")) == x:
                    correct = True
                MultipleChoiceOption.objects.create(question=q,
                                                    text=choice_text,
                                                    index=x,
                                                    is_correct=correct)
                x+=1
                choice_text = form.cleaned_data.get("choice_%d" % x)

        return HttpResponseRedirect(self.get_success_url())


class QuestionEditView(LoginRequiredMixin,
                       ContribRequiredMixin,
                       DevelopmentMixin,
                       CurrentAppMixin,
                       generic.UpdateView):
    """
    UpdateView for a user to edit an existing Question
    """
    pk_url_kwarg = 'question_id'
    
    def get_success_url(self):
        return reverse('exam:detail', args=[self.object.exam.id], current_app=self.current_app)


class FreeResponseEditView(QuestionEditView):
    model = FreeResponseQuestion
    fields = ['question','image']
    template_name = 'exam/fr_edit.html'
    
    @transaction.atomic()
    @reversion.create_revision()
    def form_valid(self,form):
        return super(FreeResponseEditView,self).form_valid(form)
    
class MultipleChoiceEditView(QuestionEditView):
    model = MultipleChoiceQuestion
    form_class = MultipleChoiceEditForm
    template_name = 'exam/mc_edit.html'

    def get_context_data(self, **kwargs):
        """
        builds a list of (choice_field,index_field) tuples
        """
        context = super(MultipleChoiceEditView, self).get_context_data(**kwargs)
        form = self.get_form(self.form_class)
        fields = list(form)
        #   fields[2] is a ChoiceField for marking the correct answer
        #   fields[3::2] is all choice_%d fields; fields[4::2] is all index_%d fields
        #   We zip these into one list so that the template can get a tuple for all fields
        #   pertaining to a single choice
        context['choice_fields'] = zip(fields[3::2], list(fields[2]), fields[4::2])
        return context


class QuestionVersionView(LoginRequiredMixin,
                          ContribRequiredMixin,
                          DevelopmentMixin,
                          CurrentAppMixin,
                          generic.UpdateView):
    pk_url_kwarg = 'question_id'
    template_name = 'exam/versions.html'
    
    def get_success_url(self):
        return reverse('exam:detail', args=[self.exam.id], current_app=self.current_app)


class FreeResponseVersionView(QuestionVersionView):
    model = FreeResponseQuestion
    form_class = FreeResponseVersionForm
    
    def get_context_data(self, **kwargs):
        context = super(FreeResponseVersionView, self).get_context_data(**kwargs)
        context['question_type'] = 'fr'
        context['version_list'] = self.object.get_unique_versions()
        return context


class MultipleChoiceVersionView(QuestionVersionView):
    model = MultipleChoiceQuestion
    form_class = MultipleChoiceVersionForm
    
    def get_option_list(self):
        """
        Returns a list of lists of MultipleChoiceOptions, oldest version first.
        e.g. l[0] is all MCOs associated with the oldest version.
        
        List is reversed so that when items are popped from the list in the template,
        the latest version will come first.
        """
        l=[]
        option_type = ContentType.objects.get_for_model(MultipleChoiceOption)
        for version in reversed(self.object.get_unique_versions()):
            option_versions = version.revision.version_set.filter(content_type__pk=option_type.id)
            options = list(version.object_version.object for version in option_versions)
            options.sort(cmp=lambda x,y: cmp(x.index, y.index))
            l.append(options)
        return l
        
    def get_context_data(self, **kwargs):
        context = super(MultipleChoiceVersionView, self).get_context_data(**kwargs)
        context['question_type'] = 'mc'
        context['version_list'] = self.object.get_unique_versions()
        context['option_list'] = self.get_option_list()
        return context


class QuestionDeleteView(LoginRequiredMixin,
                         ContribRequiredMixin,
                         DevelopmentMixin,
                         CurrentAppMixin,
                         generic.DeleteView):
    """
    "Abstract" view subclassed by FreeResponse and MultipleChoice versions.
    
    Deletes a Question, and also deletes all related revisions (deleted question can't be recovered).
    
    The reason for deleting revisions is that if a new question is created, it can be assigned
    the same pk that a deleted question had, in which case its list of revisions will include
    revisions from the deleted question.
    """
    pk_url_kwarg = 'question_id'
    template_name = 'exam/delete_question.html'
    
    def delete(self, request, *args, **kwargs):
        versions = reversion.get_for_object(self.get_object())
        self.get_object().delete()
        for version in versions:
            version.revision.delete()
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse('exam:detail', args=[self.exam.id], current_app=self.current_app)

class FreeResponseDeleteView(QuestionDeleteView):
    model = FreeResponseQuestion

class MultipleChoiceDeleteView(QuestionDeleteView):
    model = MultipleChoiceQuestion


class FinalizeView(LoginRequiredMixin,
                   StaffRequiredMixin,
                   DevelopmentMixin,
                   CurrentAppMixin,
                   SessionWizardView):
    form_list = [FinalizeSelectForm,
                 FinalizeOrderForm,
                 FinalizeConfirmForm]
    # these templates all extend exam/finalize.html
    template_list = ['exam/finalize_select.html',
                     'exam/finalize_order.html',
                     'exam/finalize_confirm.html']

    def get_template_names(self):
        return [self.template_list[int(self.steps.current)]]
    
    def get_form_instance(self, step):
        return self.exam
    
    def get_form_kwargs(self, step):
        kwargs = super(FinalizeView, self).get_form_kwargs(step)
        if step is None:
            step = self.steps.current
        if step == '1':
            kwargs['selected_questions']=self.get_cleaned_data_for_step('0').get('select_questions')
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super(FinalizeView, self).get_context_data(**kwargs)
        context['exam'] = self.exam
        if self.steps.current =='0':
            form = self.get_form()
            context['choices_and_objects'] = zip(form['select_questions'], form['select_questions'].field.queryset)
        if self.steps.current == '1':
            form = self.get_form()
            option_list = []
            for question in reversed(form.queryset):
                if question.is_multiple_choice:
                    option_list.append(question.multiplechoiceoption_set.all())
                else:
                    option_list.append([])
            context['option_list'] = option_list
        if self.steps.current == '2':
            data = self.get_all_cleaned_data()
            questions = {}
            for question in data.get('select_questions'):
                questions[data.get('question_%d'%question.id)] = question
            ordered_questions = sorted(questions.items(), key=operator.itemgetter(0))
            context['ordered_questions'] = zip(*ordered_questions)[1]
        return context

    def done(self, form_list, **kwargs):
        data = self.get_all_cleaned_data()
        for question in self.exam.question_set.all():
            if question in data.get('select_questions'):
                question.number = data.get('question_%d'%question.id)
                question.save()
            else:
                question.delete()
        self.exam.stage = ExamStage.DIST
        self.exam.save()
        return HttpResponseRedirect(reverse('exam:index', current_app=self.current_app))



################################ DISTRIBUTION and RESULTS ##################################

def respSetStats(qStats):
    """
    returns list of stats for a response set by putting together a list of stats from each question (qstats)
    list format is:
    ["Questions: ##", "Correct Answers:  ##", "Average Score: ##", "Highest Score: ##", "Lowest Score: ##"]
    """
    if (qStats):
        numQuestions = qStats[0][0]
        numCorrect = 0
        maxScore = 0
        lowScore = 100
        medianScore = 0
        for stats in qStats:
            if(stats):
                numCorrect+=stats[1]
                if (numQuestions < stats[0]):
                    numQuestions = stats[0]
                if (maxScore < stats[2]):
                    maxScore = stats[2]
                if (lowScore > stats[2]):
                    lowScore = stats[2]
        medianScore = numCorrect / float(numQuestions * len(qStats))
        medianScore = medianScore *10000 //1 /100
        return ["Questions: " + numQuestions.__str__(), "Correct answers: " + numCorrect.__str__(), "Average Score: " + medianScore.__str__(), "Highest Score: " + maxScore.__str__(), "Lowest Score: " + lowScore.__str__()]
    else:
        return [0,0,0,0,0]
    

def qstats(mcRespSet):
    """
    processes a multiplechoiceresponse_set for an exam and
    returns a list with [numquestions, numcorrect, percent correct]
    """
    numQuestions = 0
    numCorrect = 0
    for question in mcRespSet:
        
        numQuestions+=1
        if question.option_id == question.question.correct_option.id:     #later if option_id == correct_id
            numCorrect+=1
    if (numQuestions != 0):
        percCorrect = numCorrect/float(numQuestions)
        percFormatted = percCorrect * 10000 //1 /100
        return [numQuestions, numCorrect, percFormatted]
    

class ResponseSetIndexView(LoginRequiredMixin,
                           CurrentAppMixin,
                           DistributionMixin,
                           generic.TemplateView):
    """
    View to display all ResponseSets for a given exam
    """
    template_name = 'exam/response_set_index.html'

    def get_context_data(self, **kwargs):
        context = super(ResponseSetIndexView, self).get_context_data(**kwargs)
        context['exam'] = self.exam
        context['responses'] = self.exam.responseset_set.all()
        return context


class ResponseSetDetailView(LoginRequiredMixin,
                            CurrentAppMixin,
                            DistributionMixin,
                            generic.DetailView):
    """
    Detail page for a ResponseSet.
    Displays results from submitted exams.
    """
    template_name = 'exam/response_set_detail.html'
    pk_url_kwarg = 'rs_id'
    model = ResponseSet
    
    def set_stats(self):
        responses = self.object.examresponse_set.all().order_by('respondent')
        stats = []
        if not self.exam.is_survey():
            for mcrs in responses:
                stats.append(qstats(mcrs.multiplechoiceresponse_set.all()))
            set_stats = respSetStats(stats)
        else:
            set_stats = []
            for frset in responses:
                stats.append(frset.freeresponseresponse_set.all())
        return set_stats
    
    def get_context_data(self, **kwargs):
        context = super(ResponseSetDetailView, self).get_context_data(**kwargs)
        context['exam'] = self.exam
        context['response_set'] = self.object
        context['responses'] = self.object.examresponse_set.filter(submitted__isnull=False)
        context['pending'] = self.object.examresponse_set.filter(submitted__isnull=True)
        context['stats'] = self.set_stats()
        context['user_is_uploader_or_staff'] =\
            (self.request.user.is_staff or self.request.user.profile==self.object.instructor)
        return context


class ExamResponseDetailView(LoginRequiredMixin,
                             CurrentAppMixin,
                             DistributionMixin,
                             generic.DetailView):
    template_name = 'exam/exam_response_detail.html'
    model = ExamResponse
    pk_url_kwarg = 'key'
    
    def make_question_list(self):
        multiple_choice_responses = self.object.multiplechoiceresponse_set.all()
        free_response_responses = self.object.freeresponseresponse_set.all()
        question_list = []
        for question in self.object.response_set.exam.question_set.all():
            if question.is_multiple_choice:
                response = multiple_choice_responses.get(question=question)
                q = {'question':question, 'chosen':response.option_id}  #name of question; answer chosen
                qOptions = []
                qOptions.extend(question.multiplechoiceoption_set.all())
                q['options']=qOptions
                question_list.append(q)
            else:
                response = free_response_responses.get(question=question)
                q = {'question':question, 'answer':response.response}
                question_list.append(q)
        return question_list
    
    def get_context_data(self, **kwargs):
        context = super(ExamResponseDetailView, self).get_context_data(**kwargs)     
        context['exam'] = self.exam
        context['response'] = self.object
        context['stats'] = qstats(self.object.multiplechoiceresponse_set.all())
        context['question_list'] = self.make_question_list()
        return context
    

class NewResponseSetView(LoginRequiredMixin,
                         DistributionMixin,
                         CurrentAppMixin,
                         generic.FormView):
    """
    Creates a new ResponseSet object.  This view is similar to a CreateView.
    
    When a contributor wants to distribute an exam, this page records information
    specific to that distribution.  It redirects to DistributeView, which is where
    emails are provided and the exam is sent out.
    
    attributes:
        exam - refers to the exam being distributed. This is set in the dispatch
            function, and comes from the url
        object - refers to the created ResponseSet. This is set in the form_valid
            function.
            
    TODO: incorporate modules
    """
    template_name = 'exam/distribute_new.html'
    form_class = NewResponseSetForm
    
    def get_context_data(self, **kwargs):
        """
        Pass exam object to template
        """
        context = super(NewResponseSetView, self).get_context_data(**kwargs)
        context['exam'] = self.exam
        context['responses'] = self.exam.responseset_set.filter(instructor=self.request.user.profile)
        return context

    def get_success_url(self):
        return reverse('exam:responses', args=(self.object.id,), current_app=self.current_app)
    
    def form_valid(self, form):
        """
        This is where the ResponseSet is created.
        
        TODO: process selected modules from form
        """
        course = form.cleaned_data.get('course')
        pre_test = form.cleaned_data.get('pre_test')
        # modules = ...
        self.object=ResponseSet.objects.create(instructor=self.request.user.profile,
                                               course=course,
                                               pre_test=pre_test,
                                               exam=self.exam,
                                               # modules = ... 
                                               )
        return HttpResponseRedirect(self.get_success_url())


class DistributeView(LoginRequiredMixin,
                     UserPassesTestMixin,
                     CurrentAppMixin,
                     DistributionMixin,
                     generic.FormView):
    """
    View for sending ExamResponses. After a ResponseSet is created, this is
    where emails addresses are entered and the ExamResponses are sent.

    This page also provides details about a ResponseSet. It displays which email
    addresses have submitted responses and which have yet to submit. Unsubmitted
    ExamResponses can be resent; doing so deletes the pending ER and creates a new one.
    
    This view is similar to the generic UpdateView and DetailView.
    """
    template_name = 'exam/distribute_send.html'
    form_class = DistributeForm
    
    raise_exception = True
    redirect_unauthenticated_users = True
    
    def test_func(self, user):
        """
        This function is used by the UserPassesTestMixin.
        Make sure that the user is staff or the original distributor.
        """
        response_set = get_object_or_404(ResponseSet, pk=self.kwargs['rs_id'])
        return (user.is_staff or user.profile==response_set.instructor)
    
    def dispatch(self, *args, **kwargs):
        """
        Get the ResponseSet id from the url
        """
        self.object = get_object_or_404(ResponseSet, pk=self.kwargs['rs_id'])
        return super(DistributeView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """
        Pass ResponseSet object and submitted ER list to template
        """
        context = super(DistributeView, self).get_context_data(**kwargs)
        context['object'] = self.object
        context['submitted_exams'] = self.object.examresponse_set.filter(submitted__isnull=False)
        return context
    
    def get_success_url(self):
        return reverse('exam:responses',kwargs={'rs_id':self.object.id},current_app=self.current_app)
    
    def get_form_kwargs(self):
        """
        Pass ResponseSet object to form as 'instance' (like an UpdateForm)
        """
        kwargs = super(DistributeView, self).get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs
    
    def form_valid(self, form):
        """
        Create new ExamResponses and *QuestionResponses for each email address listed.
        
        TODO: apply filter by modules
        """
        # Get submitted data from form
        date = form.cleaned_data.get('expiration_date')
        time = form.cleaned_data.get('expiration_time')
        expiration_datetime = datetime.datetime.combine(date, time)
        to_send = form.cleaned_data.get('recipients') # a list of email strings
        
        # For each ExamResponse to be re-sent, delete the existing ER and add its
        # email to the list of emails to_send.
        for response in form.cleaned_data.get('resend'): # a list of ExamResponses
            to_send.append(response.respondent)
            response.delete()
            
        # For each email in the recipient list, create a new ExamResponse and create
        # associated FreeResponse- and MultipleChoiceResponses for every question
        # in the selected modules.
        for email in to_send:
            
            # If there is already an ExamResponse for this email, do not make a new one.
            # This situation will arise if an email is given twice in the recipients field.
            if not self.object.examresponse_set.filter(respondent__exact=email):
                exam_response = ExamResponse.objects.create(response_set=self.object,
                                                            respondent=email,
                                                            expiration_datetime=expiration_datetime)
                # TODO: instead of all(), filter by module
                for question in self.object.exam.freeresponsequestion_set.all():
                    FreeResponseResponse.objects.create(question=question,
                                                        exam_response=exam_response)
                for question in self.object.exam.multiplechoicequestion_set.all():
                    MultipleChoiceResponse.objects.create(question=question,
                                                      exam_response=exam_response)
                exam_response.send(self.request, email)    
        return HttpResponseRedirect(self.get_success_url())


class DeleteView(LoginRequiredMixin,
                 UserPassesTestMixin,
                 CurrentAppMixin,
                 DistributionMixin,
                 generic.DeleteView):
    """
    Confirm that an instructor would like to delete a ResponseSet. This exists in
    case an instructor accidentally creates a ResponseSet they did not intend to create.
    This will delete all associated ExamResponses and their respectice *QuestionResponses,
    so this should not be done if students have already submitted responses.
    
    A ResponseSet can only be deleted by its associated instructor or a staff user.
    """
    model = ResponseSet
    pk_url_kwarg = 'rs_id'
    template_name = 'exam/delete_responses.html'
    
    raise_exception = True
    redirect_unauthenticated_users = True
    
    def test_func(self, user):
        """
        This function is required by the UserPassesTestMixin.
        Requires that the user is staff or the original uploader
        """
        response_set = get_object_or_404(ResponseSet, pk=self.kwargs['rs_id'])
        return (user.is_staff or user.profile==response_set.instructor)

    def get_success_url(self):
        return reverse('exam:response_sets',kwargs={'exam_id':self.object.exam.id},current_app=self.current_app)


class CleanupView(LoginRequiredMixin,
                  StaffuserRequiredMixin,
                  generic.FormView):
    """
    A view for staff to manually delete expired, unsubmitted ExamResponses.
    
    This cleanup does not happen automatically, but this S.O. post suggests a good design,
    in case automatic cleanup is desired.  http://stackoverflow.com/a/11789141
    """
    template_name = 'exam/cleanup.html'
    form_class = CleanupForm
    success_url = reverse_lazy('distribute_cleanup')
    
    def get_context_data(self, **kwargs):
        """
        Pass the list of expired, unsubmitted ERs to the template
        """
        context = super(CleanupView, self).get_context_data(**kwargs)
        context['expired'] = ExamResponse.objects.filter(
            expiration_datetime__lt=timezone.now()).filter(submitted__isnull=True)
        return context
    
    def form_valid(self, form):
        """
        Delete expired, unsubmitted ERs. This also deletes the associated *QuestionResponses.
        """
        for exam_response in ExamResponse.objects.filter(
            expiration_datetime__lt=timezone.now()).filter(submitted__isnull=True):
                exam_response.delete()
        return HttpResponseRedirect(self.get_success_url())



############################# TAKE TEST ##################################################

#def TakeTestIRBView(request, pk):
#    """
#    TODO: make CBV, check that the exam is available (as in TakeTestView)
#    """
#    template = loader.get_template('exam/take_test_IRB.html')
#    context = RequestContext(request,
#                             { 'pk':pk},)
#    return HttpResponse(template.render(context))

class TakeTestIRBView(generic.DetailView):
    model = ExamResponse
    template_name = 'exam/take_test_IRB.html'

    def dispatch(self, *args, **kwargs):
        """
        Check that the ExamResponse is available.
        """
        try:
            if self.get_object().is_available():
                return super(TakeTestIRBView, self).dispatch(*args, **kwargs)
        except Http404:
            pass
        return HttpResponseRedirect(reverse('exam_unavailable'))
    
class TakeTestView(generic.UpdateView):
    """
    This is where students take the Exam. A student will get a URL that ends with the
    key to a specific ExamResponse. If that ER has expired or already been submitted, or
    if there is no exam with the given key, then the student will be redirected to an
    "Exam Unavailable" page.
    
    TODO: this template should not have the navbar (probably should not extend base.html)
    """
    model = ExamResponse
    template_name='exam/take_test.html'
    form_class = ExamResponseForm
    
    def dispatch(self, *args, **kwargs):
        """
        Check that the ExamResponse is available.
        """
        try:
            if self.get_object().is_available():
                return super(TakeTestView, self).dispatch(*args, **kwargs)
        except Http404:
            pass
        return HttpResponseRedirect(reverse('exam_unavailable'))
        
    def form_valid(self, form):
        """
        Mark the time the exam has been submitted, and call the form's save() method,
        which saves the responses.
        """
        form.save()
        self.object.submitted = timezone.now()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('exam:response_complete', current_app=self.current_app)