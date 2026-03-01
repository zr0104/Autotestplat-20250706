
delURL = 'testreport/del/'
delFieldNames = ["id"]

modURL = 'testreport/mod/'
modRowIndex = [0, 1, 2, 3, 4, 5]
testreportDetailRUL = 'getTestReportDetail/'

getSearchSelectURL = ''
getSelectURL = ''
searchableTableColumns = [0,2,3]

tableURL = 'testreport/getTableData/'
table = 0
tableButtonOperation = "<a href=\"#\" onclick=\"document.location.href = testreportDetailRUL + testreport_id(this)\"><span class=\"badge badge-primary \" style=\"width: 40px;font-size: 12px\">详情</a>"+
                       "<a href=\"#\" class=\"#\" onclick=\"showDelModal(this)\"> <span class=\"badge badge-danger \" style=\"width: 40px;font-size: 12px\">删除</span> </a>"
tableItemsPerPage = 10
tableColumnsData = [
 { data: 0 ,
   searchable:true,
 },
  { data: 1,
    searchable:true,
  },
  { data: 4,
    searchable:true,
  },
  { data: 5,
    searchable:false,
  },
  { data: 2,
    searchable:false,
  },
     { data: 3,
    searchable:false,
  },
     { data: 6,
    searchable:false,
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
    laydate.render({
        elem: '#date_Search',
        type: 'date',
        format: 'yyyy-MM-dd',
    });
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

function testreport_id(e) {
    window.event.stopPropagation()
    selectedRow = e.parentNode.parentNode
    testreport_id = selectedRow.children[0].innerText
    $("[name=caseTitle]").text("测试报告 [" + testreport_id + "] 详情")
    console.log(testreport_id)
    return testreport_id
}