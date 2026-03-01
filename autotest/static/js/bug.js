addURL = 'bug/add/'
addFieldNames = ["bug_name", "level", "bug_description","assigned_to"]
addRequiredFields = [0, 1, 2,3]

modURL = 'bug/mod/'
modFieldNames = ["id","bug_name", "level", "bug_description","assigned_to","status"]
modRequiredFields = [0, 1, 2,3,4,5]
modRowIndex = [0, 1, 2, 3,5,7]

delURL = 'bug/del/'
delFieldNames = ["id"]

getSearchSelectURL = ''
getSelectURL = ''
searchableTableColumns = [1,2,3]

tableURL = 'bug/getTableData/'
table = 0
tableButtonOperation = "<a href=\"#\" class=\"#\" onclick=\"showModModal(this)\"> <span class=\"badge badge-primary \" style=\"width: 40px;font-size: 12px\">修改</span> </a>\
                        <a href=\"#\" class=\"#\" onclick=\"showDelModal(this)\"> <span class=\"badge badge-danger \" style=\"width: 40px;font-size: 12px\">删除</span> </a>"
tableItemsPerPage = 10
tableColumnsData = [
 { data: 0 ,
   searchable:false,
 },
  { data: 1,
    searchable:true,
  },
  { data: 2,
    searchable:true,
  },
  { data: 3,
    searchable:true,
  },
  { data: 4,
    searchable:true,
  },
      { data: 8,
    searchable:true,
  },
      { data: 6,
    searchable:true,
  },
      { data: 9,
    searchable:true,
  },
      { data: 10,
    searchable:true,
  },
         { data: 7,
    searchable:true,
  },
  { data: null,
    orderable: false,
    render: function(data){
      return tableButtonOperation
    },
    searchable:false,
  }
]

function infoInit(){
    tableDataInit()
}

/**
 * @param {Object} d
 */
function tableSearchDataFunction(d){
  return
}

/**
 * @returns
 */
 function additionalTips(type = ""){
  return null
}