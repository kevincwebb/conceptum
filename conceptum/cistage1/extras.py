from nodemanager.models import ConceptNode

def close_rank_export_choices(ranking_process):
    
    choices = ranking_process.get_ranked_items_in_order()
    parent_node = ranking_process.parent
    parent_info = parent_node.ci_tree_info
        
    for choice in choices: #choice is a ConceptAtom here

        new_child = ConceptNode(
            ci_tree_info = parent_info,
            parent = parent_node,
            content = choice.text,
        )
        new_child.save()

    #once we have created the new nodes we close the ranking process
    ranking_process.status = ranking_process.closed
    ranking_process.save()

    #and advance the state of the parent node
    parent_node.transition_node_state()
    parent_node.save()
    
    return
