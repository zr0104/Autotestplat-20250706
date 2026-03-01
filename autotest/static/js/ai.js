

function infoInit(){
    // getAndShowSearchSelectValue()
    // getAndShowAddSelectValue()
    // getAndShowModSelectValue()
    // getAndShowSetSelectValue()
    tableDataInit()
}

function tableSearchDataFunction(d){
  d.user_name = $("[name=searchField]").eq(0).val()
}


 function additionalTips(type = ""){
  return null
}
