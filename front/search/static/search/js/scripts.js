/** 
 * get parameters from the GET method URL.
 * @return {dictionary[string|Array[string]]} The dictionary of the parameter names and their values.
 */
function getUrlParam(){
    let params = {};
    if (1 < window.location.search.length){
        // get string except first character: '?';
        const paramUrl = window.location.search.substring(1);

        const param_list = paramUrl.split('&');
        for (let i = 0; i < param_list.length; i++){
            const element = param_list[i].split('=');

            const paramName = decodeURIComponent(element[0]);
            const paramValue = decodeURIComponent(element[1]);

            // 連想配列の作成。
            // 同じparamが複数ある場合にはArrayで格納。
            if (params[paramName] == null){
                params[paramName] = paramValue;
            } else if (Array.isArray(params[paramName])){
                params[paramName].push(paramValue);
            } else {
                // arrayに変換。
                params[paramName] = [params[paramName], paramValue];
            }
        }
    }
    return params;
}

/** 
 * GETパラメータの言語情報を反映する関数。
 * @param {string|Array[string]} param_lr: GET parameter of the language.
 */
function reflectLRParam(param_lr){
    if (param_lr != null){
        let checkbox_lr = document.getElementsByName("lr");
        console.log(param_lr);
        if (Array.isArray(param_lr)){
            for (let i = 0; i < checkbox_lr.length; i++){
                checkbox_lr[i].checked = (param_lr.includes(checkbox_lr[i].value));
            }
        } else {
            for (let i = 0; i < checkbox_lr.length; i++){
                checkbox_lr[i].checked = (param_lr == checkbox_lr[i].value);
            }
        }
    }
}

/** 
 * MathJaxで書かれた数式を変換する関数。
 * @param {object} canvas: 数式を保持している要素。
 */
function renderMath(canvas){
    MathJax.typeset([canvas]);
}

/** 
 * 2つ以上のspaceをqueryの区切り文字として複数のqueryを区切る関数。
 * @param {string} inputText: queries.
 * @return {Array[string]} 
 */
function splitQueries(inputText) {
    return inputText.split(/ {2,}/g);
}

/** 
 * クエリ毎にspanタグで区切り、renderする関数。
 * @param {string} inputText: queries.
 */
function inputChange(){
    const inputText = document.getElementById("inputText");
    const queries = splitQueries(inputText.value);
    const canvas = document.getElementById("canvas");
    canvas.innerHTML = "";
    for(let i = 0; i < queries.length; i++) {
        canvas.innerHTML += "<span>" + "\\(" + queries[i] + "\\)" + "</span>";
    }
    renderMath(canvas);
}

/** 
 * query中のspaceを処理する関数。
 * space1つは%20に、space2つ以上はspace1つに変換する。
 * TODO: ' 'のencodeについて考える。
 * @param {string} inputText: queries.
 * @return {string}
 */
function makeQueryString(inputText) {
    let queries = splitQueries(inputText);

    let queryString = "";
    for(let i = 0; i < queries.length; i++) {
        // space1つをencodeする。
        queries[i] = queries[i].replace(/ /, encodeURI(" "));

        queryString += queries[i];
        if(i + 1 < queries.length) {
            queryString += " ";
        }
    }

    return queryString;
}

/** 
 * スクリーンキーボードで押された数式をキャレットの位置に挿入する関数。
 * @param {string} expr: スクリーンキーボードで押された数式。
 */
function insertExpr(expr){
    const text = document.getElementById("inputText");

    const tmpText = text.value.substring(0, text.selectionStart) + expr;
    text.value = tmpText + text.value.substring(text.selectionStart);

    const caretIndex = tmpText.length;
    text.focus();
    text.setSelectionRange(caretIndex, caretIndex);

    inputChange();
}

/** 
 * formをsubmitする関数。
 */
function submit(){
    let form = document.createElement('form');
    form.action = '.';
    form.method = 'GET';

    const inputText = document.getElementById("inputText");

    let q = document.createElement('input');
    q.value = makeQueryString(inputText.value);
    q.name = 'q';
    q.type = 'hidden';
    q.formenctype = 'text/plain';
    form.appendChild(q);

    const lr = document.getElementById("lang");
    form.appendChild(lr);

    document.body.appendChild(form);

    form.submit();
}


document.addEventListener('DOMContentLoaded', function(){
    const tabs = document.getElementsByClassName('tab');
    for(let i = 0; i < tabs.length; i++) {
        tabs[i].addEventListener('click', switchTab, false);
    }

    // Enterで検索できるようにする。
    window.document.onkeydown = function(event){
        if (event.key === 'Enter') {
            submit();
        }
    }

    /** 
     * スクリーンキーボードのタブ・パネルを切り替える関数。
     */
    function switchTab(){
        // is-activeの切り替え
        document.getElementsByClassName('is-active')[0].classList.remove('is-active');
        this.classList.add('is-active');

        // is-showの切り替え
        document.getElementsByClassName('is-show')[0].classList.remove('is-show');
        // is-showにするパネルのindexを探す
        for(var i = 0; i < tabs.length; i++) {
            if (tabs[i] == this) {
                break;
            }
        }
        document.getElementsByClassName('panel')[i].classList.add('is-show');
    };

}, false);
