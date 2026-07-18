addURL = 'aitestcase/addAitestcase/'
addFieldNames = ['ai_testcase_name', 'ai_testcase_step', 'ai_testcase_stepname','ai_testcase_expect_value']
addRequiredFields = [0,1, 2]

modURL = 'aitestcase/modAitestcase/'
modFieldNames = ['ai_testcase_code','ai_testcase_name', 'ai_testcase_result',  'ai_testcase_step', 'ai_testcase_stepname', 'ai_testcase_expect_value', 'ai_testcase_real_value','ai_testcase_step_result','requirements_id']
modRequiredFields = [0, 1, 2, 3,4]
modRowIndex = [0, 1, 2, 3]

copyURL = 'aitestcase/copyAitestcase/'
copyFieldNames = ['ai_testcase_name', 'ai_testcase_result',  'ai_testcase_step', 'ai_testcase_stepname', 'ai_testcase_expect_value', 'ai_testcase_real_value','ai_testcase_step_result']
copyRequiredFields = [0, 2, 3,4]
copyRowIndex = [0, 1, 2, 3]

runURL = 'aitestcase/runAitestcase/'
runFieldNames = ['ai_testcase_name', 'ai_testcase_result']
runRequiredFields = [0, 1]
runRowIndex = [0, 1]

delURL = 'aitestcase/delAitestcase/'
delFieldNames = ['ai_testcase_code']

// 覆盖 public.js 中的 showDelModal，修正复选框列导致的索引偏移
function showDelModal(e){
    selectedRow = e.parentNode.parentNode
    var inputFields = $("[name=delInput]")
    // children[0]=复选框, children[1]=用例编号, children[2]=用例名称
    if(inputFields[0] && inputFields[0].tagName == "INPUT"){
        inputFields[0].value = selectedRow.children[1].innerText
    }
    if(inputFields[1] && inputFields[1].tagName == "INPUT"){
        inputFields[1].value = selectedRow.children[2].innerText
    }
    $("#deleteModal").modal('show')
    window.event.stopPropagation()
}

runAiTestcaseBycode = 'aitestcase/run_aitestcase/'

testcaseDetailRUL = 'getAitestcaseDetail/'
getSearchSelectURL = ''
getSelectURL = 'aitestcase/getAiOptions/'
searchableTableColumns = [1,2,3]

tableURL = 'aitestcase/getTableData/'
table = 0
tableButtonOperation = "<a href=\"#\" class=\"#\" onclick=\"showRun(this)\"> <span class=\"badge badge-success \" style=\"width: 40px;font-size: 12px\">执行</span> </a>" +
                       "<a href=\"#\" class=\"#\" onclick=\"showMod(this)\"> <span class=\"badge badge-primary \" style=\"width: 40px;font-size: 12px\">修改</span> </a>" +
                       "<a href=\"#\" class=\"#\" onclick=\"showCopy(this)\"> <span class=\"badge badge-blue \" style=\"width: 40px;font-size: 12px\">复制</span> </a>" +
                       "<a href=\"#\" class=\"#\" onclick=\"showDelModal(this)\"> <span class=\"badge badge-danger \" style=\"width: 40px;font-size: 12px\">删除</span> </a>"
tableItemsPerPage = 10
var selectedCodes = [];

tableColumnsData = [
                    { data: null,
                      orderable: false,
                      searchable: false,
                      render: function(data, type, row) {
                        var checked = selectedCodes.indexOf(row[0]) >= 0 ? ' checked' : '';
                        return '<input type="checkbox" class="row-checkbox" value="' + row[0] + '"' + checked + ' style="cursor:pointer;">';
                      },
                      width: '40px'
                    },
                    { data: 0 },
                    { data: 1,
                      searchable:true,
                    },
                    { data: 2,
                      searchable:true,
                      render: function(data, type, row) {
                        var val = data || '未执行';
                        var color = val === 'pass' ? '#28a745' : val === 'fail' ? '#dc3545' : '#6c757d';
                        return '<select class="form-control form-control-sm result-select" data-code="' + row[0] + '" style="padding:2px 4px;font-size:12px;border-color:' + color + ';color:' + color + ';font-weight:bold;">' +
                          '<option value="未执行"' + (val === '未执行' ? ' selected' : '') + '>未执行</option>' +
                          '<option value="pass"' + (val === 'pass' ? ' selected' : '') + '>pass</option>' +
                          '<option value="fail"' + (val === 'fail' ? ' selected' : '') + '>fail</option>' +
                          '</select>';
                      }
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
                    { data: null,
                      render: function(data){
                        return tableButtonOperation
                      },
                      searchable:false,
                    }
                ]

function infoInit(){
    selectedCodes = [];
    aiCaseTableDataInit()
    table.on('draw', function() {
        updateSelectedCount();
        var selectAll = document.getElementById('selectAll');
        if (selectAll) {
            selectAll.checked = (selectedCodes.length > 0 && selectedCodes.length === table.rows().count());
        }
    });
    $('#table tbody').on('change', '.row-checkbox', function() {
        var code = $(this).val();
        var isChecked = $(this).is(':checked');
        var idx = selectedCodes.indexOf(code);

        if (isChecked && idx < 0) {
            selectedCodes.push(code);
        } else if (!isChecked && idx >= 0) {
            selectedCodes.splice(idx, 1);
        }

        updateSelectedCount();
        var selectAll = document.getElementById('selectAll');
        if (selectAll) {
            selectAll.checked = (selectedCodes.length > 0 && selectedCodes.length === table.rows().count());
        }
    });

    $('#table tbody').on('change', '.result-select', function() {
        var code = $(this).data('code');
        var result = $(this).val();
        var color = result === 'pass' ? '#28a745' : result === 'fail' ? '#dc3545' : '#6c757d';
        $(this).css({'border-color': color, 'color': color});
        $.ajax({
            url: appURL + 'aitestcase/runAitestcase/',
            type: 'POST',
            contentType: 'application/json;charset=utf-8',
            data: JSON.stringify({rundataObj: {id1: code, ai_testcase_result: result}}),
            success: function(rst) {
                if (rst !== '200') alert('更新失败：' + rst);
            },
            error: function() { alert('更新失败！'); }
        });
    });
}

function tableSearchDataFunction(d){
  var filters = $("[name=searchField]")
  var searchData = {}
  for(var i = 0; i < filters.length; i++){
      searchData['search_' + i] = filters[i].value
  }
  return searchData
}


function additionalTips(type = ""){
  return null
}

caseStepInputs = 1
caseStepInput_innerHtml = "<div class=\"input-group\" style=\"margin-bottom: 15px; width: 90%;\">\
<input name=\"addInput\" id=\"caseStep\" eleName=\"caseStep\" class=\"form-control\" placeholder=\"--请输入--\" value='第1步' style='width: 5px;height:80px;font-size: 12px' disabled></input>\
<textarea name=\"addInput\" eleName_objname=\"caseStep_objname\" class=\"form-control\" placeholder=\"--请输入--\"  style=\"width:220px;height:80px;font-size: 12px;text-align: left\"></textarea>\
<textarea name=\"addInput\" eleName_findmethod=\"caseStep_findmethod\" class=\"form-control\" placeholder=\"--请输入--\" style=\"width:220px;height:80px;font-size: 12px;text-align: left\"></textarea>\
</div>\
<div>\
<button class=\"btn btn-primary\" style=\"width: 40px; margin-left: 10px;\" onclick=\"addCaseStepInput(this)\"> + </button>\
<button class=\"btn btn-danger\" style=\"width: 40px; margin-left: 5px;\" onclick=\"subCaseStepInput(this)\"> - </button>\
</div>"

modcaseStepInputs = 1
modcaseStepInput_innerHtml = "<div class=\"input-group\" style=\"margin-bottom: 15px; width: 90%;\">\
<input name=\"modInput\" id=\"caseStep\" mod_eleName=\"caseStep\" class=\"form-control\" placeholder=\"--请输入--\" value='第1步' style='width: 5px;height:80px;font-size: 12px' disabled></input>\
<textarea name=\"modInput\" mod_eleName_objname=\"caseStep_objname\" class=\"form-control\" placeholder=\"--请输入--\"  style=\"width:120px;height:80px;font-size: 12px;text-align: left\"></textarea>\
<textarea name=\"modInput\" mod_eleName_findmethod=\"caseStep_findmethod\" class=\"form-control\" placeholder=\"--请输入--\"  style='width: 30px;height:80px;font-size: 12px' ></textarea>\
</div>\
<div>\
<button class=\"btn btn-primary\" style=\"width: 40px; margin-left: 10px;\" onclick=\"addModCaseStepInput(this)\"> + </button>\
<button class=\"btn btn-danger\" style=\"width: 40px; margin-left: 5px;\" onclick=\"subModCaseStepInput(this)\"> - </button>\
</div>"


copycaseStepInputs = 1
copycaseStepInput_innerHtml = "<div class=\"input-group\" style=\"margin-bottom: 15px; width: 90%;\">\
<input name=\"copyInput\" id=\"caseStep\" copy_eleName=\"caseStep\" class=\"form-control\" placeholder=\"--请输入--\" value='第1步' style='width: 5px;height:80px;font-size: 12px' disabled></input>\
<textarea name=\"copyInput\" copy_eleName_objname=\"caseStep_objname\" class=\"form-control\" placeholder=\"--请输入--\"  style=\"width:120px;height:80px;font-size: 12px;text-align: left\"></textarea>\
<textarea name=\"copyInput\" class=\"form-control\" id=\"caseStep_findmethod\" copy_eleName_findmethod=\"caseStep_findmethod\" style=\"width:112px;height:80px;font-size: 12px;text-align: left\"></textarea>\
</div>\
<div>\
<button class=\"btn btn-primary\" style=\"width: 40px; margin-left: 10px;\" onclick=\"addCopyCaseStepInput(this)\"> + </button>\
<button class=\"btn btn-danger\" style=\"width: 40px; margin-left: 5px;\" onclick=\"subCopyCaseStepInput(this)\"> - </button>\
</div>"


function showAdd(){
  var addModal = $("#addModal")
  var inputFields = addModal.find("[name=addInput]")
  for(var i = 0; i < inputFields.length; i++){
      var temp = inputFields[i]
      if(temp.tagName == "INPUT" || temp.tagName == "TEXTAREA"){
          temp.value = ''
      }
      else if(temp.tagName == "SELECT"){
          $(temp).find("option[selected=true]").prop("selected",false)
          $(temp).find("option").eq(0).prop("selected",true)
      }
  }
  caseStepInputs = 1
  addCaseStepListDiv = document.getElementsByName("addCaseStepList")[0]
  addCaseStepListDiv.innerHTML = ""
  var ele1 = document.createElement('div')
  ele1.setAttribute('class', 'row')
  ele1.innerHTML = caseStepInput_innerHtml
  addCaseStepListDiv.appendChild(ele1)
  addModal.modal('show')
  addObjects()
  window.event.stopPropagation()
}

function showMod(ele){
    selectedRow = ele.parentNode.parentNode
    ai_testcase_code = selectedRow.children[1].innerText
    ai_testcase_name = selectedRow.children[2].innerText
    requirements_id = selectedRow.children[7].innerText

    // 初始化自定义下拉框
    var dropdown = document.getElementById('modRequirementDropdown');
    var reqInput = document.getElementById('modRequirementInput');
    var reqArrow = document.getElementById('modRequirementArrow');
    if (dropdown && reqInput) {
        dropdown.innerHTML = '';
        dropdown.style.display = 'none';
        reqInput.value = '';
        reqArrow.textContent = '▼';

        reqInput.onclick = function(e) {
            e.stopPropagation();
            if (dropdown.style.display === 'none') {
                dropdown.style.display = 'block';
                reqArrow.textContent = '▲';
            } else {
                dropdown.style.display = 'none';
                reqArrow.textContent = '▼';
            }
        };

        document.onclick = function(e) {
            if (!dropdown.contains(e.target) && e.target !== reqInput) {
                dropdown.style.display = 'none';
                reqArrow.textContent = '▼';
            }
        };

        $.ajax({
            url: '/autotest/requirements/getTableData/',
            type: 'POST',
            success: function(resp) {
                if (resp && resp.data) {
                    resp.data.forEach(function(item) {
                        var div = document.createElement('div');
                        div.style.cssText = 'padding: 8px 12px; cursor: pointer; border-bottom: 1px solid #f0f0f0; font-size: 13px;';
                        div.textContent = item[0] + ' - ' + (item[1] || '未命名需求');
                        div.onmouseover = function() { this.style.backgroundColor = '#e8f4fd'; };
                        div.onmouseout = function() { this.style.backgroundColor = '#fff'; };
                        div.onclick = function(e) {
                            e.stopPropagation();
                            reqInput.value = this.textContent;
                            dropdown.style.display = 'none';
                            reqArrow.textContent = '▼';
                        };
                        dropdown.appendChild(div);
                    });
                }
                if (requirements_id && requirements_id.trim()) {
                    reqInput.value = requirements_id;
                    if (resp && resp.data) {
                        resp.data.forEach(function(item) {
                            if (String(item[0]) === String(requirements_id)) {
                                reqInput.value = item[0] + ' - ' + (item[1] || '未命名需求');
                            }
                        });
                    }
                }
            },
            error: function() {
                if (requirements_id && requirements_id.trim()) {
                    reqInput.value = requirements_id;
                }
            }
        });
    }

    $.ajax({
        url: "/autotest/aitestcase/showModAiTestcase/",
        data: JSON.stringify({
            id1: ai_testcase_code,
            name1: ai_testcase_name,
            requirements_id1: requirements_id,
        }),
        contentType: 'application/json;charset=utf-8',
        type: "POST",
        traditional: true,
        success: function (result) {
            $('#modModal').find('.modal-title').text('编辑测试用例：' + ai_testcase_code);
            document.getElementsByName('modInput')[0].value = ai_testcase_name;
            var case_steps = result['case_step_list'].split(',');
            var objname = result['objname'].split(',');
            console.log(objname)
            var findmethod = result['findmethod'].split(',');
            modcaseStepInputs = 0
            modCaseStepListDiv = document.getElementsByName("modCaseStepList")[0]
            modCaseStepListDiv.innerHTML = ""
            for (var i = 0; i < case_steps.length; i++) {
                var tmp_append = '<div class="input-group" style="margin-bottom: 15px; width: 90%;" xmlns="http://www.w3.org/1999/html" >'+
                            '<input name="modInput" id="caseStep" mod_eleName="caseStep" class="form-control" placeholder="--请输入--" value='+case_steps[i]+' style="width:5px;height:80px;font-size:12px" disabled></input>'+
                            '<textarea name="modInput" mod_eleName_objname="caseStep_objname" class="form-control" placeholder="--请输入--" style="width:120px;height:80px;font-size:12px;text-align:left">'+objname[i]+'</textarea>'+
                           '<textarea name="modInput" mod_eleName_findmethod="caseStep_findmethod" class="form-control" placeholder="--请输入--" style="width:120px;height:80px;font-size:12px;text-align:left">'+findmethod[i]+'</textarea>'+
                           '</div>'+
                        '<div>'+
                           '<button class="btn btn-primary" style="width: 40px; margin-left: 10px;" onclick="addModCaseStepInput(this)"> + </button>'+
                           '<button class="btn btn-danger" style="width: 40px; margin-left: 5px;" onclick="subModCaseStepInput(this)"> - </button>'+
                        '</div>';
                var ele1 = document.createElement('div')
                ele1.setAttribute('class', 'row')
                ele1.innerHTML = tmp_append
                modCaseStepListDiv.appendChild(ele1)
            }
            $('#modModal').modal();
            modObjects()
            window.event.stopPropagation()
            },
        fail: function (result) {
            debugger
        }
    });
}


function showCopy(ele){
    selectedRow = ele.parentNode.parentNode
    ai_testcase_code = selectedRow.children[1].innerText
    ai_testcase_name = selectedRow.children[2].innerText
    requirements_id = selectedRow.children[7] ? selectedRow.children[7].innerText : '';

    // 初始化自定义下拉框
    var dropdown = document.getElementById('copyRequirementDropdown');
    var reqInput = document.getElementById('copyRequirementInput');
    var reqArrow = document.getElementById('copyRequirementArrow');
    if (dropdown && reqInput) {
        dropdown.innerHTML = '';
        dropdown.style.display = 'none';
        reqInput.value = '';
        reqArrow.textContent = '▼';

        reqInput.onclick = function(e) {
            e.stopPropagation();
            if (dropdown.style.display === 'none') {
                dropdown.style.display = 'block';
                reqArrow.textContent = '▲';
            } else {
                dropdown.style.display = 'none';
                reqArrow.textContent = '▼';
            }
        };

        document.onclick = function(e) {
            if (!dropdown.contains(e.target) && e.target !== reqInput) {
                dropdown.style.display = 'none';
                reqArrow.textContent = '▼';
            }
        };

        $.ajax({
            url: '/autotest/requirements/getTableData/',
            type: 'POST',
            success: function(resp) {
                if (resp && resp.data) {
                    resp.data.forEach(function(item) {
                        var div = document.createElement('div');
                        div.style.cssText = 'padding: 8px 12px; cursor: pointer; border-bottom: 1px solid #f0f0f0; font-size: 13px;';
                        div.textContent = item[0] + ' - ' + (item[1] || '未命名需求');
                        div.onmouseover = function() { this.style.backgroundColor = '#e8f4fd'; };
                        div.onmouseout = function() { this.style.backgroundColor = '#fff'; };
                        div.onclick = function(e) {
                            e.stopPropagation();
                            reqInput.value = this.textContent;
                            dropdown.style.display = 'none';
                            reqArrow.textContent = '▼';
                        };
                        dropdown.appendChild(div);
                    });
                }
                if (requirements_id && requirements_id.trim()) {
                    reqInput.value = requirements_id;
                    if (resp && resp.data) {
                        resp.data.forEach(function(item) {
                            if (String(item[0]) === String(requirements_id)) {
                                reqInput.value = item[0] + ' - ' + (item[1] || '未命名需求');
                            }
                        });
                    }
                }
            },
            error: function() {
                if (requirements_id && requirements_id.trim()) {
                    reqInput.value = requirements_id;
                }
            }
        });
    }

    $.ajax({
        url: "/autotest/aitestcase/showCopyAiTestcase/",
        data: JSON.stringify({
            id1: ai_testcase_code,
            name1: ai_testcase_name,
        }),
        contentType: 'application/json;charset=utf-8',
        type: "POST",
        traditional: true,
        success: function (result) {
            $('#copyModal').find('.modal-title').text('复制测试用例：' + ai_testcase_code);
            document.getElementsByName('copyInput')[0].value = ai_testcase_name;
            var case_steps = result['case_step_list'].split(',');
            var objname = result['objname'].split(',');
            var findmethod = result['findmethod'].split(',');

            copycaseStepInputs = 0
            copyCaseStepListDiv = document.getElementsByName("copyCaseStepList")[0]
            copyCaseStepListDiv.innerHTML = ""
            for (var i = 0; i < case_steps.length; i++) {
                var tmp_append = '<div class="input-group" style="margin-bottom: 15px; width: 90%;" xmlns="http://www.w3.org/1999/html" >'+
                            '<input name="copyInput" id="caseStep" copy_eleName="caseStep" class="form-control" placeholder="--请输入--" value='+case_steps[i]+' style="width:5px;height:80px;font-size:12px" disabled></input>'+
                            '<textarea name="copyInput" copy_eleName_objname="caseStep_objname" class="form-control" placeholder="--请输入--" style="width:120px;height:80px;font-size:12px;text-align:left">'+objname[i]+'</textarea>'+
                           '<textarea name="copyInput" copy_eleName_findmethod="caseStep_findmethod" class="form-control" placeholder="--请输入--" style="width:120px;height:80px;font-size:12px;text-align:left">'+findmethod[i]+'</textarea>'+
                           '</div>'+
                        '<div>'+
                           '<button class="btn btn-primary" style="width: 40px; margin-left: 10px;" onclick="addCopyCaseStepInput(this)"> + </button>'+
                           '<button class="btn btn-danger" style="width: 40px; margin-left: 5px;" onclick="subCopyCaseStepInput(this)"> - </button>'+
                        '</div>';
                var ele1 = document.createElement('div')
                ele1.setAttribute('class', 'row')
                ele1.innerHTML = tmp_append
                copyCaseStepListDiv.appendChild(ele1)
            }
            $('#copyModal').modal();
            copyObjects()
            window.event.stopPropagation()
            },
        fail: function (result) {
            debugger
        }
    });
}


function showRun(ele){
    selectedRow = ele.parentNode.parentNode
    ai_testcase_code = selectedRow.children[1].innerText
    ai_testcase_name = selectedRow.children[2].innerText
    var resultSelect = selectedRow.children[3].querySelector('select');
    ai_testcase_result = resultSelect ? resultSelect.value : '未执行';
    $.ajax({
        url: "/autotest/aitestcase/showRunAiTestcase/",
        data: JSON.stringify({
            id1: ai_testcase_code,
            name1: ai_testcase_name,
            order1: ai_testcase_result,
        }),
        contentType: 'application/json;charset=utf-8',
        type: "POST",
        traditional: true,
        success: function (result) {
            $('#runModal').find('.modal-title').text('运行测试用例：' + ai_testcase_code);
            document.getElementsByName('runInput')[0].value = ai_testcase_name;
            document.getElementsByName('runInput')[1].value = ai_testcase_result;
            $('#runModal').modal();
            modObjects()
            window.event.stopPropagation()
            },
        fail: function (result) {
            debugger
        }
    });
}


function addCaseStepInput(e){
  var ele1 = document.createElement('div')

  ele1.setAttribute('class', 'row')
  ele1.innerHTML = caseStepInput_innerHtml

  e.parentNode.parentNode.parentNode.insertBefore(ele1, e.parentNode.parentNode.nextSibling)
  caseStepInputs += 1

  var rowNumberElement = $("[eleName]")
  for (i=0;i<rowNumberElement.length;i++){
      var j=i+1;
      rowNumberElement[i].value = "第"+j+"步";
  }
}

function subCaseStepInput(e){
  if(caseStepInputs == 1){
    alert("至少保留一个输入框")
    return
  }

  e.parentNode.parentNode.parentNode.removeChild(e.parentNode.parentNode)
  caseStepInputs -= 1

  var rowNumberElement = $("[eleName]")
  for (i=0;i<rowNumberElement.length;i++){
      var j=i+1;
      rowNumberElement[i].value = "第"+j+"步";
  }
}


function addModCaseStepInput(e){
  var ele1 = document.createElement('div')

  ele1.setAttribute('class', 'row')
  ele1.innerHTML = modcaseStepInput_innerHtml

  e.parentNode.parentNode.parentNode.insertBefore(ele1, e.parentNode.parentNode.nextSibling)
  modcaseStepInputs += 1

  var rowNumberElement = $("[mod_eleName]")
  for (i=0;i<rowNumberElement.length;i++){
      var j=i+1;
      rowNumberElement[i].value = "第"+j+"步";
  }
}

function subModCaseStepInput(e){
  if(modcaseStepInputs == 1){
    alert("至少保留一个输入框")
    return
  }

  e.parentNode.parentNode.parentNode.removeChild(e.parentNode.parentNode)
  modcaseStepInputs -= 1

  var rowNumberElement = $("[mod_eleName]")
  for (i=0;i<rowNumberElement.length;i++){
      var j=i+1;
      rowNumberElement[i].value = "第"+j+"步";
  }
}

function addCopyCaseStepInput(e){
  var ele1 = document.createElement('div')

  ele1.setAttribute('class', 'row')
  ele1.innerHTML = copycaseStepInput_innerHtml

  e.parentNode.parentNode.parentNode.insertBefore(ele1, e.parentNode.parentNode.nextSibling)
  copycaseStepInputs += 1

  var rowNumberElement = $("[copy_eleName]")
  for (i=0;i<rowNumberElement.length;i++){
      var j=i+1;
      rowNumberElement[i].value = "第"+j+"步";
  }
}

function subCopyCaseStepInput(e){
  if(copycaseStepInputs == 1){
    alert("至少保留一个输入框")
    return
  }

  e.parentNode.parentNode.parentNode.removeChild(e.parentNode.parentNode)
  copycaseStepInputs -= 1

  var rowNumberElement = $("[copy_eleName]")
  for (i=0;i<rowNumberElement.length;i++){
      var j=i+1;
      rowNumberElement[i].value = "第"+j+"步";
  }
}

function addSave(tips="新增成功"){
  var inputFields = $("[name=addInput]")
  for(var i = 0; i < addRequiredFields.length; i++){
      if(inputFields[addRequiredFields[i]].value == ''){
          return alert("*信息为必填项！")
      }
  }
  $.ajax({
      url: appURL + addURL,
      type: "POST",
      aysnc: false,
      data: addObjects(),
      success: (rst) => {
          if(rst === '200'){
              operationSelectValue('add')
              alert(tips)
              $("#addModal").modal('hide')
          }
          else{
              return alert(rst)
          }
      },
      error: (rst) =>{
          return alert(rst)
      },
  })
}

function modSave(tips="修改成功"){
  var inputFields = $("[name=modInput]")
  for(var i = 0; i < modRequiredFields.length; i++){
      console.log(inputFields[modRequiredFields[i]].value)
      if(inputFields[modRequiredFields[i]].value == ''){
          return alert("*信息为必填项！")
      }
  }
  $.ajax({
      url: appURL + modURL,
      type: "POST",
      aysnc: false,
      data: modObjects(),
      success: (rst) => {
          if(rst === '200'){
              operationSelectValue('modify')
              alert(tips)
              $("#modModal").modal('hide')
          }
          else{
              return alert(rst)
          }
      },
      error: (rst) =>{
          return alert('保存失败！')
      },
  })
}


function copySave(tips="复制成功"){
  var inputFields = $("[name=copyInput]")
  for(var i = 0; i < copyRequiredFields.length; i++){
      if(inputFields[copyRequiredFields[i]].value == ''){
          return alert("*信息为必填项！")
      }
  }
  $.ajax({
      url: appURL + copyURL,
      type: "POST",
      async: false,
      contentType: 'application/json;charset=utf-8',
      data: copyObjects(),
      success: (rst) => {
          if(rst === '200'){
              operationSelectValue('copy')
              alert(tips)
              $("#copyModal").modal('hide')
          }
          else{
              return alert(rst)
          }
      },
      error: (rst) =>{
          return alert('复制失败！')
      },
  })
}



function runSave(tips="运行成功"){
  var inputFields = $("[name=runInput]")

  for(var i = 0; i < runRequiredFields.length; i++){
      if(inputFields[runRequiredFields[i]].value == ''){
          return alert("*信息为必填项！")
      }
  }
  $.ajax({
      url: appURL + runURL,
      type: "POST",
      aysnc: false,
      data: runObjects(),
      success: (rst) => {
          if(rst === '200'){
              operationSelectValue('modify')
              alert(tips)
              $("#runModal").modal('hide')
          }
          else{
              return alert(rst)
          }
      },
      error: (rst) =>{
          return alert('保存失败！')
      },
  })
}


function run_aitestcase_bycode(e,tips="运行成功"){
  selectedRow = e.parentNode.parentNode
  ai_testcase_code = selectedRow.children[0].innerText

  $.ajax({
      url: appURL + runAiTestcaseBycode+ai_testcase_code,
      type: "POST",
      aysnc: false,
      data: function(dp){
                dp.ai_testcase_code = ai_testcase_code
            },
      success: (rst) => {
          if(rst === '200'){
              alert(tips)
              $("#addModal").modal('hide')
          }
          else{
              return alert(rst)
          }
      },
      error: (rst) =>{
          return alert('运行有误，请检查appium或uiautomator2的安装配置、系统设置中App设置、手机连接设置等信息是否正确 !')
      },
  })
}

function run_aitestcase_byproduct(e,tips="运行成功"){
  $.ajax({
      url: appURL + runAiTestcaseByProduct,
      type: "POST",
      aysnc: false,
      data: function(dp){
            },
      success: (rst) => {
          if(rst === '200'){
              alert(tips)
              $("#addModal").modal('hide')
          }
          else{
              return alert(rst)
          }
      },
      error: (rst) =>{
          return alert('运行有误，请检查appium或uiautomator2的安装配置、系统设置中App设置、手机连接设置等信息是否正确 !')
      },
  })
}


function aitestcase_code(e) {
    window.event.stopPropagation()
    selectedRow = e.parentNode.parentNode
    ai_testcase_code = selectedRow.children[0].innerText
    return ai_testcase_code
}

function addObjects(){
  caseStepFields = $("[name=addInput]").not("[eleName]")
  caseStepFields_objname = $("[name=addInput]").not("[eleName_objname]")
  caseStepFields_findmethod = $("[name=addInput]").not("[eleName_findmethod]")

  caseStepListFields = $("[eleName]")
  caseStepListFields_objname = $("[eleName_objname]")
  caseStepListFields_findmethod = $("[eleName_findmethod]")

  caseStepList = []
  caseStepList_objname = []
  caseStepList_findmethod = []

  dataObj = {}
  for(let i = 0; i < caseStepFields.length; i++){
    dataObj[addFieldNames[i]] = caseStepFields[i].value
  }
  for(let i = 0; i < caseStepFields_objname.length; i++){
    dataObj[addFieldNames[i]] = caseStepFields_objname[i].value
  }
  for(let i = 0; i < caseStepFields_findmethod.length; i++){
    dataObj[addFieldNames[i]] = caseStepFields_findmethod[i].value
  }

  for(let i = 0; i < caseStepListFields.length; i++){
    if(caseStepListFields[i].value.length > 0){
        caseStepList.push(caseStepListFields[i].value)
    }
  }
  for(let i = 0; i < caseStepListFields_objname.length; i++){
    if(caseStepListFields_objname[i].value.length > 0){
        caseStepList_objname.push(caseStepListFields_objname[i].value)
    }
  }
  for(let i = 0; i < caseStepListFields_findmethod.length; i++){
    if(caseStepListFields_findmethod[i].value.length > 0){
        caseStepList_findmethod.push(caseStepListFields_findmethod[i].value)
    }
  }

  dataObj["caseStepList"] = caseStepList
  dataObj["caseStepList_objname"] = caseStepList_objname
  dataObj["caseStepList_findmethod"] = caseStepList_findmethod

  return dataObj
}

function modObjects(){
  modcaseStepFields = $("[name=modInput]").not("[mod_eleName]")
  modcaseStepFields_objname = $("[name=modInput]").not("[mod_eleName_objname]")
  modcaseStepFields_findmethod = $("[name=modInput]").not("[mod_eleName_findmethod]")

  modcaseStepListFields = $("[mod_eleName]")
  modcaseStepListFields_objname = $("[mod_eleName_objname]")
  modcaseStepListFields_findmethod = $("[mod_eleName_findmethod]")

  modcaseStepList = []
  modcaseStepList_objname = []
  modcaseStepList_findmethod = []

  moddataObj = {}
  for(let i = 0; i < modcaseStepFields.length; i++){
    moddataObj[modFieldNames[i]] = modcaseStepFields[i].value
  }
  for(let i = 0; i < modcaseStepFields_objname.length; i++){
    moddataObj[modFieldNames[i]] = modcaseStepFields_objname[i].value
  }
  for(let i = 0; i < modcaseStepFields_findmethod.length; i++){
    moddataObj[modFieldNames[i]] = modcaseStepFields_findmethod[i].value
  }

  for(let i = 0; i < modcaseStepListFields.length; i++){
    if(modcaseStepListFields[i].value.length > 0){
        modcaseStepList.push(modcaseStepListFields[i].value)
    }
  }
  for(let i = 0; i < modcaseStepListFields_objname.length; i++){
    if(modcaseStepListFields_objname[i].value.length > 0){
        modcaseStepList_objname.push(modcaseStepListFields_objname[i].value)
    }
  }
  for(let i = 0; i < modcaseStepListFields_findmethod.length; i++){
    if(modcaseStepListFields_findmethod[i].value.length > 0){
        modcaseStepList_findmethod.push(modcaseStepListFields_findmethod[i].value)
    }
  }

  var id1 = $('#modModal').find('.modal-title')[0].textContent
  id1 = id1.split("：")[1];
  var ai_testcase_name1 = document.getElementsByName('modInput')[0].value;
  moddataObj["ai_testcase_name"] = ai_testcase_name1
  var reqInput = document.getElementById('modRequirementInput');
  var requirements_id1 = reqInput ? reqInput.value : '';
  if (requirements_id1.indexOf(' - ') > 0) {
      requirements_id1 = requirements_id1.split(' - ')[0].trim();
  }
  moddataObj["requirements_id"] = requirements_id1
  moddataObj["ai_testcase_name"] = ai_testcase_name1
  moddataObj["id1"] = id1
  moddataObj["modcaseStepList"] = modcaseStepList
  moddataObj["modcaseStepList_objname"] = modcaseStepList_objname
  moddataObj["modcaseStepList_findmethod"] = modcaseStepList_findmethod
  return JSON.stringify({moddataObj})
}


function copyObjects(){
  copycaseStepFields = $("[name=copyInput]").not("[copy_eleName]")
  copycaseStepFields_objname = $("[name=copyInput]").not("[copy_eleName_objname]")
  copycaseStepFields_findmethod = $("[name=copyInput]").not("[copy_eleName_findmethod]")

  copycaseStepListFields = $("[copy_eleName]")
  copycaseStepListFields_objname = $("[copy_eleName_objname]")
  copycaseStepListFields_findmethod = $("[copy_eleName_findmethod]")

  copycaseStepList = []
  copycaseStepList_objname = []
  copycaseStepList_findmethod = []

  copydataObj = {}
  for(let i = 0; i < copycaseStepFields.length; i++){
    copydataObj[copyFieldNames[i]] = copycaseStepFields[i].value
  }
  for(let i = 0; i < copycaseStepFields_objname.length; i++){
    copydataObj[copyFieldNames[i]] = copycaseStepFields_objname[i].value
  }
  for(let i = 0; i < copycaseStepFields_findmethod.length; i++){
    copydataObj[copyFieldNames[i]] = copycaseStepFields_findmethod[i].value
  }

  for(let i = 0; i < copycaseStepListFields.length; i++){
    if(copycaseStepListFields[i].value.length > 0){
        copycaseStepList.push(copycaseStepListFields[i].value)
    }
  }
  for(let i = 0; i < copycaseStepListFields_objname.length; i++){
    if(copycaseStepListFields_objname[i].value.length > 0){
        copycaseStepList_objname.push(copycaseStepListFields_objname[i].value)
    }
  }
  for(let i = 0; i < copycaseStepListFields_findmethod.length; i++){
    if(copycaseStepListFields_findmethod[i].value.length > 0){
        copycaseStepList_findmethod.push(copycaseStepListFields_findmethod[i].value)
    }
  }

  var id1 = $('#copyModal').find('.modal-title')[0].textContent
  id1 = id1.split("：")[1];
  var reqInput = document.getElementById('copyRequirementInput');
  var requirements_id1 = reqInput ? reqInput.value : '';
  if (requirements_id1.indexOf(' - ') > 0) {
      requirements_id1 = requirements_id1.split(' - ')[0].trim();
  }
  copydataObj["requirements_id"] = requirements_id1
  copydataObj["id1"] = id1
  copydataObj["copycaseStepList"] = copycaseStepList
  copydataObj["copycaseStepList_objname"] = copycaseStepList_objname
  copydataObj["copycaseStepList_findmethod"] = copycaseStepList_findmethod
  return JSON.stringify({copydataObj})
}


function runObjects(){
  runcaseStepFields = $("[name=runInput]").not("[run_eleName]")
  runcaseStepFields_objname = $("[name=runInput]").not("[run_eleName_objname]")
  runcaseStepFields_findmethod = $("[name=runInput]").not("[run_eleName_findmethod]")

  runcaseStepListFields = $("[run_eleName]")
  runcaseStepListFields_objname = $("[run_eleName_objname]")
  runcaseStepListFields_findmethod = $("[run_eleName_findmethod]")

  runcaseStepList = []
  runcaseStepList_objname = []
  runcaseStepList_findmethod = []


  rundataObj = {}
  for(let i = 0; i < runcaseStepFields.length; i++){
    rundataObj[runFieldNames[i]] = runcaseStepFields[i].value
  }
  for(let i = 0; i < runcaseStepFields_objname.length; i++){
    rundataObj[runFieldNames[i]] = runcaseStepFields_objname[i].value
  }
  for(let i = 0; i < runcaseStepFields_findmethod.length; i++){
    rundataObj[runFieldNames[i]] = runcaseStepFields_findmethod[i].value
  }

  for(let i = 0; i < modcaseStepListFields.length; i++){
    if(modcaseStepListFields[i].value.length > 0){
        modcaseStepList.push(modcaseStepListFields[i].value)
    }
  }
  for(let i = 0; i < runcaseStepListFields_objname.length; i++){
    if(runcaseStepListFields_objname[i].value.length > 0){
        runcaseStepList_objname.push(runcaseStepListFields_objname[i].value)
    }
  }
  for(let i = 0; i < runcaseStepListFields_findmethod.length; i++){
    if(runcaseStepListFields_findmethod[i].value.length > 0){
        runcaseStepList_findmethod.push(runcaseStepListFields_findmethod[i].value)
    }
  }

  var id1 = $('#runModal').find('.modal-title')[0].textContent
  id1 = id1.split("：")[1];
  rundataObj["id1"] = id1
  rundataObj["runcaseStepList"] = runcaseStepList
  rundataObj["runcaseStepList_objname"] = runcaseStepList_objname
  rundataObj["runcaseStepList_findmethod"] = runcaseStepList_findmethod
  return JSON.stringify({rundataObj})
}

function toggleSelectAll(el) {
    var allCodes = [];
    table.rows().every(function() {
        var data = this.data();
        if (data) allCodes.push(data[0]);
    });
    if (el.checked) {
        for (var i = 0; i < allCodes.length; i++) {
            if (selectedCodes.indexOf(allCodes[i]) < 0) selectedCodes.push(allCodes[i]);
        }
    } else {
        selectedCodes = [];
    }
    updateSelectedCount();

    // 直接操作DOM确保视觉状态同步
    $('#table tbody .row-checkbox').each(function() {
        $(this).prop('checked', el.checked);
    });
}

function updateSelectedCount() {
    var countEl = document.getElementById('selectedCount');
    if (countEl) {
        countEl.textContent = '已选 ' + selectedCodes.length + ' / 共 ' + table.rows().count() + ' 条';
    }
}

function batchRunWithStatus() {
    if (selectedCodes.length === 0) {
        alert('请先勾选需要批量执行的用例！');
        return;
    }
    var result = document.getElementById('batchResultSelect').value;
    $.ajax({
        url: appURL + 'aitestcase/batchRunAitestcase/',
        type: 'POST',
        contentType: 'application/json;charset=utf-8',
        data: JSON.stringify({ codes: selectedCodes, ai_testcase_result: result }),
        success: function(rst) {
            if (rst === '200') {
                alert('批量更新成功！已更新 ' + selectedCodes.length + ' 条用例结果为：' + result);
                selectedCodes = [];
                table.ajax.reload(null, false);
            } else {
                alert('批量更新失败：' + rst);
            }
        },
        error: function(xhr) {
            alert('批量更新失败！');
        }
    });
}
