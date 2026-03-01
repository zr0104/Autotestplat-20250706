addURL = 'worktask/add/'
addFieldNames = ["wt_datetime", "wt_thisweek", "wt_nextweek","question"]
addRequiredFields = [0, 1, 2, 3]

modURL = 'worktask/mod/'
modFieldNames = ["id","wt_datetime", "wt_thisweek", "wt_nextweek","question"]
modRequiredFields = [0, 1, 2,3,4]
modRowIndex = [0, 1, 2, 3,4]

delURL = 'worktask/del/'
delFieldNames = ["id"]

getSearchSelectURL = 'worktask/getSearchSelect/'
getSelectURL = 'worktask/getSelect/'
searchableTableColumns = [1]

tableURL = 'worktask/getTableData/'
table = 0
tableButtonOperation = "<a href=\"#\" class=\"#\" onclick=\"showModModal(this)\"> <span class=\"badge badge-primary \" style=\"width: 40px;font-size: 12px\">修改</span> </a>"
                        // <a href=\"#\" class=\"#\" onclick=\"showDelModal(this)\"> <span class=\"badge badge-danger \" style=\"width: 40px;font-size: 12px\">删除</span> </a>"
tableButtonOperationNo = "<a href=\"#\" class=\"disabled\" onclick=\"return false;\"> <span class=\"badge badge-secondary \" style=\"width: 40px;font-size: 12px\">修改</span> </a>"

tableItemsPerPage = 10
tableColumnsData = [
 { data: 0 ,
   searchable:false,
 },
  { data: 1,
    searchable:true,
  },
  { data: 2,
    searchable:false,
  },
  { data: 3,
    searchable:false,
  },
  { data: 4,
    searchable:false,
  },
  { data: 5,
    searchable:false,
    // visible: false
  },
  { data: null,
    orderable: false,
    render: function(data,type,row){
                const currentLoginAccount = JSON.parse(localStorage.getItem('user'));
                console.log(currentLoginAccount.userName)
                console.log(row[5])
                if(row[5] === currentLoginAccount.userName){
                  return tableButtonOperation
                }
                else{
                  return tableButtonOperationNo
                }
              },
    searchable:false,
  }
]

function infoInit(){
    getAndShowSearchSelectValue()
    // getAndShowAddSelectValue()
    // getAndShowModSelectValue()
    // getAndShowSetSelectValue()
    tableDataInit()
}

/**
 * @param {Object} d
 */
function tableSearchDataFunction(d){
  return null
}

/**
 * @returns
 */
 function additionalTips(type = ""){
  return null
}