addURL = 'iteration/add/'
addFieldNames = ["iteration_version", "start_time","except_end_time"]
addRequiredFields = [0, 1, 2]

modURL = 'iteration/mod/'
modFieldNames = ["id","iteration_version"]
modRequiredFields = [0, 1]
modRowIndex = [0, 1]

reportURL='iteration/report/'
reportFieldNames = ["id","iteration_version"]
reportRequiredFields = [0, 1]
reportRowIndex = [0, 1]

delURL = 'iteration/del/'
delFieldNames = ["id"]

getSearchSelectURL = ''
getSelectURL = ''
searchableTableColumns = [1,2,3]

tableURL = 'iteration/getTableData/'
table = 0
tableButtonOperation = "<a href=\"#\" class=\"#\" onclick=\"showModModal(this)\"> <span class=\"badge badge-blue \" style=\"width: 40px;font-size: 12px\">修改</span> </a>\
                        <a href=\"#\" class=\"#\" onclick=\"showDelModal(this)\"> <span class=\"badge badge-danger \" style=\"width: 40px;font-size: 12px\">删除</span> </a>\
                        <a href=\"#\" class=\"#\" onclick=\"showTestReport(this)\"> <span class=\"badge badge-blue \" style=\"width: 100px;font-size: 12px\">生成测试报告</span> </a>\
                        "
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
    { data: 5,
    searchable:true,
  },
    { data: 6,
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
