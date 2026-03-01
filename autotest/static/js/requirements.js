addURL = 'requirements/add/'
addFieldNames = ["iteration_version","requirements_name", "requirements_type"]
addRequiredFields = [0, 1, 2]

modURL = 'requirements/mod/'
modFieldNames = ["id","requirements_name","assigned_to"]
modRequiredFields = [0, 1,2]
modRowIndex = [0, 1,3]

delURL = 'requirements/del/'
delFieldNames = ["id"]

reToCaseURL = 'requirements/totestcase/'
reToCaseFieldNames = ["id","requirements_name"]
reToCaseRequiredFields = [0, 1]
reToCaseRowIndex = [0, 1]

reToCaseDetailRUL = 'getReToCaseDetail/'


getSearchSelectURL = ''
getSelectURL = ''
searchableTableColumns = [1,2,3]

tableURL = 'requirements/getTableData/'
table = 0
tableButtonOperation = "<a href=\"#\" class=\"#\" onclick=\"showReToCaseModal(this)\"> <span class=\"badge badge-blue \" style=\"width: 80px;font-size: 12px\">AI生成用例</span> </a>\
                        <a href=\"#\" class=\"#\" onclick=\"showModModal(this)\"> <span class=\"badge badge-blue \" style=\"width: 40px;font-size: 12px\">修改</span> </a>\
                        <a href=\"#\" class=\"#\" onclick=\"showDelModal(this)\"> <span class=\"badge badge-danger \" style=\"width: 40px;font-size: 12px\">删除</span> </a>\
                        <a href=\"#\" onclick=\"document.location.href = reToCaseDetailRUL + require_id(this)\"><span class=\"badge badge-primary \" style=\"width: 80px;font-size: 12px\">关联用例</a>\
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
  { data: 8,
    searchable:true,
  },
    { data: 4,
    searchable:true,
  },
        { data: 9,
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
    table.on('click', 'tbody tr', function() {
        var row = table.row(this);
        row.child(formatChildRowData(row.data())).show();
        console.log(row)
        if (row.child.isShown()) {
            // 如果子行已显示，则隐藏
            row.child.hide();
            $(this).removeClass('parent');
        } else {
            // 如果子行未显示，则显示
            row.child(formatChildRowData(row.data())).show();
            $(this).addClass('parent');
        }
    });

    function formatChildRowData(data) {
        // 根据data生成子行的HTML内容
        // 例如：
        return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'+
                '<tr><td>Details for this row:</td></tr>'+
                // '<tr><td>' +"test"+ '</td></tr>'+
                '</table>';
    }
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

function require_id(e) {
    window.event.stopPropagation()
    selectedRow = e.parentNode.parentNode
    require_id = selectedRow.children[0].innerText
    $("[name=caseTitle]").text("需求关联测试用例 [" + require_id + "] 详情")
    console.log(require_id)
    return require_id
}