
delURL = 'report/del/'
delFieldNames = ["report_id"]

modURL = 'report/mod/'
modRowIndex = [0, 1, 2, 3, 4, 5]
reportDetailRUL = 'getReportDetail/'

getSearchSelectURL = ''
getSelectURL = ''
searchableTableColumns = [0,2,3]

tableURL = 'report/getTableData/'
table = 0
tableButtonOperation = "<a href=\"#\" onclick=\"document.location.href = reportDetailRUL + report_id(this)\"><span class=\"badge badge-primary \" style=\"width: 40px;font-size: 12px\">详情</a>"+
                       "<a href=\"#\" class=\"#\" onclick=\"showDelModal(this)\"> <span class=\"badge badge-danger \" style=\"width: 40px;font-size: 12px\">删除</span> </a>"
tableItemsPerPage = 10
tableColumnsData = [
 { data: 0 ,
   searchable:true,
 },
  { data: 1,
    searchable:true,
  },
  { data: 2,
    searchable:true,
  },
  { data: 3,
    searchable:false,
  },
  { data: 4,
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
    console.log('[DEBUG] infoInit - 开始初始化');

    // 绑定左上角全局产品下拉框的变化事件
    var globalProductSelect = $('#select-option');
    if (globalProductSelect.length > 0) {
        console.log('[DEBUG] 找到左上角全局产品下拉框');

        // 记录当前选中的产品
        var currentProduct = globalProductSelect.val();
        console.log('[DEBUG] 当前全局产品:', JSON.stringify(currentProduct));

        // 绑定变化事件
        globalProductSelect.on('change', function() {
            var newProduct = $(this).val();
            console.log('[DEBUG] ========== 左上角产品切换 ==========');
            console.log('[DEBUG] 旧产品:', JSON.stringify(currentProduct));
            console.log('[DEBUG] 新产品:', JSON.stringify(newProduct));

            // 更新当前产品值
            currentProduct = newProduct;

            // 同步更新报告页面的产品下拉框（如果存在）
            var reportProductFilter = $('#product_filter');
            if (reportProductFilter.length > 0) {
                reportProductFilter.val(newProduct);
                console.log('[DEBUG] 已同步更新报告页面产品下拉框为:', JSON.stringify(newProduct));
            }

            // 触发报告表格刷新
            console.log('[DEBUG] 准备调用 searchClick() 刷新报告列表');
            searchClick();
        });
    } else {
        console.error('[ERROR] 未找到左上角全局产品下拉框 #select-option');
    }

    // 同时绑定报告页面的产品下拉框（作为备用）
    var reportProductFilter = $('#product_filter');
    if (reportProductFilter.length > 0) {
        console.log('[DEBUG] 报告页面产品下拉框存在，绑定变化事件');
        reportProductFilter.on('change', function() {
            var selectedValue = $(this).val();
            console.log('[DEBUG] 报告页面产品下拉框切换:', JSON.stringify(selectedValue));
            searchClick();
        });
    }

    tableDataInit();
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
  console.log('[DEBUG] ========== tableSearchDataFunction 被调用 ==========');

  // 优先使用左上角全局产品下拉框的值
  var globalProduct = $('#select-option').val();
  console.log('[DEBUG] 左上角全局产品值:', JSON.stringify(globalProduct));

  // 获取其他搜索条件
  var searchFields = $("[name=searchField]");
  console.log('[DEBUG] searchFields 数量:', searchFields.length);

  // 第一个 searchField 是报告ID
  if (searchFields.length >= 1) {
    d.report_id_search = searchFields[0].value || '';
    console.log('[DEBUG] [0] 报告ID搜索:', JSON.stringify(d.report_id_search));
  }

  // 第二个 searchField 是测试计划
  if (searchFields.length >= 2) {
    d.suit_name_search = searchFields[1].value || '';
    console.log('[DEBUG] [1] 测试计划搜索:', JSON.stringify(d.suit_name_search));
  }

  // 第三个 searchField 是执行时间
  if (searchFields.length >= 3) {
    d.date_time_search = searchFields[2].value || '';
    console.log('[DEBUG] [2] 执行时间搜索:', JSON.stringify(d.date_time_search));
  }

  // 第四个 searchField 是产品（id="product_filter"）
  if (searchFields.length >= 4) {
    d.product_filter = searchFields[3].value || '';
    console.log('[DEBUG] [3] 产品过滤值（从searchFields）:', JSON.stringify(d.product_filter));
  }

  // 使用全局产品值覆盖（如果全局产品有值）
  if (globalProduct && globalProduct !== '') {
    d.product_filter = globalProduct;
    console.log('[DEBUG] [最终] 使用全局产品值覆盖 product_filter:', JSON.stringify(d.product_filter));
  }

  console.log('[DEBUG] 最终传递给后端的完整参数对象:', JSON.stringify(d, null, 2));
  console.log('[DEBUG] ========================================');
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

