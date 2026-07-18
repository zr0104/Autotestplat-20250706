// autotest/static/js/webreport.js

delURL = 'webreport/del/'
delFieldNames = ["report_id"]

modURL = 'webreport/mod/'
modRowIndex = [0, 1, 2, 3, 4, 5]
reportDetailRUL = 'getWebReportDetail/'

getSearchSelectURL = ''
getSelectURL = ''
searchableTableColumns = [0,2,3]

tableURL = 'webreport/getTableData/'
table = 0
tableButtonOperation = "<a href=\"#\" onclick=\"document.location.href = reportDetailRUL + report_id(this)\"><span class=\"badge badge-primary \" style=\"width: 40px;font-size: 12px\">详情</a>"+
                       "<a href=\"#\" class=\"#\" onclick=\"showDelModal(this)\"> <span class=\"badge badge-danger \" style=\"width: 40px;font-size: 12px\">删除</span> </a>"
tableItemsPerPage = 10
tableColumnsData = [
 { data: 0 ,
   searchable:true,
 },
  { data: 3,
    searchable:true,
  },
  { data: 7,
    searchable:false,
  },
  { data: 5,
    searchable:false,
    render: function(data){
        if(data === 'pass'){
            return '<span style="color:green;font-weight:bold;">pass</span>'
        }else if(data === 'fail'){
            return '<span style="color:red;font-weight:bold;">fail</span>'
        }
        return data
    }
  },
  { data: 6,
    searchable:false,
    render: function(data){
        if(data === '100%'){
            return '<span style="color:green;font-weight:bold;">100%</span>'
        }else if(data === '0%'){
            return '<span style="color:red;font-weight:bold;">0%</span>'
        }
        return data
    }
  },
  { data: 4,
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
  var filters = $("[name=searchField]")
  var searchData = {}
  for(var i = 0; i < filters.length; i++){
      searchData['search_' + i] = filters[i].value
  }
  return searchData
}

/**
 * @returns
 */
 function additionalTips(type = ""){
  return null
}

function report_id(e) {
    window.event.stopPropagation()
    selectedRow = e.parentNode.parentNode
    report_id = selectedRow.children[0].innerText
    $("[name=caseTitle]").text("测试报告 [" + report_id + "] 详情")
    console.log(report_id)
    return report_id
}
