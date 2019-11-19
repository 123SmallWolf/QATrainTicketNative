let xmlHttp;


//键盘监听
function onKeyDown(str){ //str
    let e = window.event||window;
    if(e.key=== "Enter" && e.ctrlKey){
        document.getElementById("search").value += "\n";
    }
    else if(e.key === "Enter"){
        sendMessage(str);
        e.preventDefault();
    }
}

//发送一个消息
function sendMessage(str){
    if(str===""){return}
    //添加信息
    document.getElementById('talk').innerHTML +=
    `<div class="me" style="clear: both">
        <div class="i-talk">
            <div class="me-chat">我</div>
            <div class="content">${str}</div>
            <span class="i-talk-cor"></span>
        </div>
    </div>`;
    //清空输入框
    let search = document.getElementById('search');
    search.value = '';

    xmlHttp = GetXmlHttpObject();
    if (xmlHttp == null) {
        alert("恭喜您，您的浏览器不支持ajax！");
        return;
    }

    // let datas = JSON.stringify({"utterance": str, "token": ""});
    let datas = {"utterance": str, "token": ""};
    // console.log(datas)

    $.ajax({
       url: "http://127.0.0.1:5000/register_Response",
       type: 'POST',
       data: datas,
       success: function(data){
           console.log(data);
           document.getElementById('talk').innerHTML +=
               `<div class="robot" style="clear: both">
                    <div class="chat">
                        <div class="robot-icon" style="width:46px;height: 46px;"></div>
                        <div class="robot-response">
                            <div class="robot-chat">
                                ${data.utterance}
                            </div>
                        </div>
                        <span class="robot-talk-cor"></span>
                    </div>
                </div>`;
           let hid=document.getElementById('msg_end');
           hid.scrollIntoView(false);

       },
       error: function (data){
           console.log(data);
           alert("失败")
       }
    });
    let hid2=document.getElementById('msg_end');
    hid2.scrollIntoView(false);
}

function GetXmlHttpObject(){
    let xmlHttp=null;
    try{
        xmlHttp=new XMLHttpRequest();
    }catch(e){
        try{
            xmlHttp=new ActiveXObject("Msxml2.XMLHTTP");
        }catch(e){
            xmlHttp=new ActiveXObject("Microsoft.XMLHTTP");
        }
    }
    return xmlHttp;
}