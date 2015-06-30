/* Project specific Javascript goes here. */



function PlusMinus(ckbx)
{
   if( ckbx.checked )
   {
      document.getElementById("minus").style.display = "inline-block";
      document.getElementById("plus").style.display = "none";
   }
   else
   {
      document.getElementById("minus").style.display = "none";
      document.getElementById("plus").style.display = "inline-block";
   }

}


