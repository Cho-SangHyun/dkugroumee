$(document).ready(function(){
  let long_events = $('.long-event-container');
  $.each(long_events,function(index, item){
    let x_start = item.getAttribute('xstart');
    let y_start = item.getAttribute('ystart');;
    let size = item.getAttribute('xsize');
    
    let c_value = x_start + ' / span ' + size;
    item.style.gridColumn = c_value;
    item.style.gridRow = y_start;

    let children = item.childNodes;
    
    for(let i=0; i<children.length; i++){
      if(children[i].nodeName !== "#text"){
        if(children[i].getAttribute('is_event') === "True"){
          children[i].style.backgroundColor = children[i].getAttribute('selected_color')
        }
      }
    }
  });
  let long_events_color = $('.long-event-container').find('div[is_event="True"]').attr("selected_color")
  // $('.long-event-container').find('div[is_event="True"]').css("backgroundColor", this.attr("selected_color"));
  $('.long-event-container').find('div[is_first="True"]').css("border-top-left-radius", "5px");
  $('.long-event-container').find('div[is_first="True"]').css("border-bottom-left-radius", "5px");
  $('.long-event-container').find('div[is_last="True"]').css("border-top-right-radius", "5px");
  $('.long-event-container').find('div[is_last="True"]').css("border-bottom-right-radius", "5px");

  let short_events = $('.short-event-container');
  $.each(short_events,function(index, item){
    let x_start = item.getAttribute('xstart');
    let y_start = item.getAttribute('ystart');
    let size = item.getAttribute('xsize');

    let c_value = x_start + ' / span ' + size;
    item.style.gridColumn = c_value;
    item.style.gridRow = y_start;

    let children = item.childNodes;
    
    for(let i=0; i<children.length; i++){
      if(children[i].nodeName !== "#text"){
        if(children[i].getAttribute('is_event') === "True"){
          children[i].style.color = children[i].getAttribute('selected_color')
        }
      }
    }
  });

  $(".day").click(function () {                     // 어떤 날짜를 누르면 이하 내용들을 실행
                                                           /* ★★★실행시키고자 하는 것★★★
                                                              : 특정 날짜를 누르면 그 날짜에 테두리가 생기고
                                                                사이드바가 나오는데, 그 바에는 그 날에 해당
                                                                하는 일정들과 일정들의 개수, 클릭한 날짜, 새
                                                                일정 생성 버튼이 있다.  */ 
    $(".day").css("border", "0");                                                              
    $(".day").css("borderBottom", "1px solid rgba(166, 168, 179, 0.12)");                   // 다른 날짜들에 있는 테두리를 없애고
    $(".day").css("borderRight", "1px solid rgba(166, 168, 179, 0.12)");
    $(this).css("border", "3px solid rgb(185, 190, 235)")       // 클릭한 날짜에 테두리가 생긴다. 

    let day = $(this).html().split('<')[0];          // 클릭한 날짜의 날(ex : 15, 17, 31...)을 가져와서
    $("#cur_day").text(day);                         // 사이드바의 날짜로 한다. 즉 클릭한 날짜가 사이드바에 표시되게 됨

    let date = new Date(cur_year + '-' + cur_month + '-' + day);                 // 클릭한 날짜
    let week = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"];
    $("#cur_weekday").text(week[date.getDay()]);                                 // 클릭한 날짜의 요일 영어로 해서 

    let param = {                                    // 클릭한 날짜의 년/월/일을 객체형태로. 얘를 ajax통신에 사용할 것임
      'year' : cur_year,
      'month' : cur_month,
      'day' : day
    }

    $.ajax({                                         // ajax 통신
      url : show_userschedule_url,                   // 통신할 url. urlspy에서 이 url에 매칭되는 views가 실행됨
      type : 'POST',                                 // 어떤 방식으로 통신할 것인지. GET or POST
      headers : {
        'X-CSRFTOKEN' : csrf_token
      },
      data : JSON.stringify(param),                  // 보낼 데이타. 객체 param을 json형태로 바꿔줬음
      success:function(data){                        // 통신에 성공하면 이하 내용 실행. 파라미터 data는 view에서 넘겨받은 것임

        let schedules_list = JSON.parse(data);                            // view에서 받은 json형태의 데이터를 js객체형태로 바꿔서 할당
                                                                          // 즉 schedules_list는 js객체들의 리스트형태
                                                                          // ex) [json_data_01, json_data_02, json_data_03, ...]
                                                                          // shcedules_list는 클릭한 날짜의 일정들의 리스트임
        $(".content-section").empty();                      // 일정들이 채워질 영역을 비움 -> 7일날 일정 보다가 8일 일정 볼때, 7일 일정
                                                            // 은 날리고 8일 일정만 봐야 하므로 

        if (!schedules_list.length){
          $(".content-section").append(                                    // 사이드바에 일정 추가
            '<div class="is-not-schedule">\
              <i class="fas fa-calendar-times"></i>\
              <p>아무 일정도 없습니다.<br>새 일정을 추가해보세요!</p>\
            </div>'
          );
        }
        else{                                                 // schedules_list의 사이즈가 0아 이니라면 
          for(let i=0; i<schedules_list.length; i++){         // 각 일정들을 실실적으로 사이드바에 추가할 것임
          let start_time = schedules_list[i]['fields']['start'].split('T');
          start_time = start_time[0] + ' ' + start_time[1].slice(0, 5);   // start_time : 그 일정의 시작 시간 ex) 2021-07-16 19:00

          let end_time = schedules_list[i]['fields']['end'].split('T');
          end_time = end_time[0] + ' ' + end_time[1].slice(0, 5);         // end_time : 그 일정의 종료 시간 ex) 2021-07-16 21:30

          let time = start_time + ' ~ ' + end_time;                       
          let content = schedules_list[i]['fields']['title'].slice(0, 20);  // content : 그 일정의 내용, 단 20글자만 가져옴

          let corner_color = schedules_list[i]['fields']['color'];
          console.log(corner_color)
  
          $(".content-section").append(                                    // 사이드바에 일정 추가
            '<div class="content" corner_color="' + corner_color + '">\
              <div class="top">\
                <div>' + time + '</div>\
                <i class="fas fa-edit edit-schedule" data-bs-toggle="modal" data-bs-target="#UserScheduleModal" value="' + schedules_list[i]['pk'] + '"></i>\
                <i class="fas fa-trash-alt delete-schedule" value="' + schedules_list[i]['pk'] + '"></i>\
              </div>\
              <div class="mid">' 
                + content
              + '</div>\
            </div>'
          );
          }

          let contents = $('.content');

          $.each(contents,function(index, item){
            let corner_color = item.getAttribute('corner_color');
            item.style.background = "linear-gradient(135deg, " + corner_color + " 7%, #fff 0)";
          });
        }
      },
      error:function(){                              // 통신에 실패하면 이하 내용 실행
        alert("데이터를 가져오는데 실패했습니다");
      }
    });                                             // ajax 통신 종료

    $("#Sidebar").css("right", "0");                 // 사이드바 나오게 하기
  });
  // js를 통해 동적으로 만든 요소들에는 일반적인 이벤트가 동작되지 않음 -> 밑에 주석처리한 코드를 주석해제해도 .content를 클릭할 시 아무일도 일어나지 않음

  // $(".content-section .content").click(function (){
  //   alert("야호");
  // });
  let schedule_id_for_edit; // 수정할 스케줄의 pk값을 담을 변수, 얘를 url에 넘겨서 사용할 것임
  // 동적으로 생성된 요소들에 대한 이벤트는 밑에 코드처럼 활용해야 한다
  $(document).on("click", ".edit-schedule", function(){             // 각 스케줄들의 수정 아이콘(연필모양)을 누르면 이하 내용 실행
                                                                    // 부트스트랩 연동으로 모달창이 자동으로 띄워지는데, 모달창의 폼을 우리가 수정할 스케줄의 값들로 채울 것임
    $('.modal-title').text('일정 수정');
    $('.btn-wrapper .save-btn').text('수정');
    $('.btn-wrapper .save-btn').attr("id", "edit-userschedule");  // 모달의 이름과 버튼이름, 버튼의 아이디값을 설정

    $('.modal-body #userschedule-form ul').empty();                   // 오류메시지 출력하는 칸도 비움

    schedule_id_for_edit = $(this).attr("value");                     // 클릭한 스케줄의 pk값을 할당

    $.ajax({
      url : ("/usercalendar/edit/" + schedule_id_for_edit + '/'),
      type : 'GET',
      success:function(data){
        $('#id_start_date').val(data['start_date']);
        $('#id_start_hour').val(data['start_hour']);
        $('#id_start_minute').val(data['start_minute']);
        $('#id_end_date').val(data['end_date']);
        $('#id_end_hour').val(data['end_hour']);
        $('#id_end_minute').val(data['end_minute']);
        $('#id_title').val(data['title']);
        $('#id_color').val(data['color']);                             // 수정할 스케줄의 원래 값들을 폼에 담아줌
      },
      error:function(){
        alert("일정을 불러오는데 실패했습니다");
      },
    });

  });

  $(document).on("click", "#edit-userschedule", function(){            // 모달에서 수정버튼을 누르면 이하 내용 실행
    const start_date = document.getElementById("id_start_date").value;
    const start_hour = $("#id_start_hour option:selected").val();
    const start_minute = $("#id_start_minute option:selected").val();
    const end_date = document.getElementById("id_end_date").value;
    const end_hour = $("#id_end_hour option:selected").val();
    const end_minute = $("#id_end_minute option:selected").val();
    const title = document.getElementById("id_title").value;
    const color = document.getElementById("id_color").value;
    const csrf = document.getElementsByName('csrfmiddlewaretoken');

    const fd = new FormData();

    fd.append('csrfmiddlewaretoken', csrf[0].value);
    fd.append('start_date', start_date);
    fd.append('start_hour', start_hour);
    fd.append('start_minute', start_minute);
    fd.append('end_date', end_date);
    fd.append('end_hour', end_hour);
    fd.append('end_minute', end_minute);
    fd.append('title', title);
    fd.append('color', color);                                         // 입력한 폼 데이터들을 전부 fd란 변수에 담아서 ajax통신
    
    $.ajax({
      url : ("/usercalendar/edit/" + schedule_id_for_edit + '/'),
      type : 'POST',
      headers : {
        'X-CSRFTOKEN' : csrf_token
      },
      data : fd,
      success:function(data){

        if(data['result'] === "success"){                   // 작성한 폼이 유효했다면 redirect
          setTimeout(function() {
            location.href = "";
          }, 300);
        }
        else{                                               // 작성한 폼이 유효 X -> 에러메시지 출력
          form_errors = JSON.parse(data['form_errors']);    // json형태의 데이터를 js객체형태로 바꿔줌

          $('#userschedule-form ul').empty();               // 오류메시지 출력하는 부분 비우기
         
          $.each(form_errors, function(i, value){           // 2중 반복문을 돌며 오류 메시지 각 영역에 채우기
            $.each(value, function(j, message){
              let error_message = '<li>' + value[j]['message'] + '</li>';
              let error_field = i.split('_')[0]
              $("ul[id*='" + error_field +"']").append(error_message);
            });
          });
        }

      },
      error:function(){
        alert("일정을 수정하는데 실패했습니다");
      },
      cache : false,
      contentType: false,
      processData: false
    });

  });

  $(".go-add-userschedule").click(function (){               // 스케줄 추가 아이콘을 누르면 이하 내용들 실행
                                                             // 자동으로 띄워지는 모달창의 폼 양식을 설정할 건데, 시작시간과 종료시간을 클릭된 날짜로 할 것임
    $('.modal-title').text('새 일정 생성');
    $('.btn-wrapper .save-btn').text('내 캘린더에 추가하기');    // 디자인 적용 위해 save-btn으로 변경
    $('.btn-wrapper .save-btn').attr("id", "add-userschedule");    // 모달의 이름과 버튼이름, 버튼의 아이디값을 설정

    $('.modal-body #userschedule-form ul').empty();                    // 오류메시지 출력하는 영역 비우기
    // let form_field_month = (cur_month < 10) ? ("0" + cur_month) : cur_month;
    // let form_field_day = (day < 10) ? ("0" + day) : day;
    // 폼 필드 중 start, end의 기본값을 세팅할 것임. 클릭한 날짜를 기준. 시간, 분은 00시 00분으로 설정
    let form_field_month = cur_month.padStart(2, '0');            // month가 10보다 작으면 앞에 0을 붙임 ex) 7 -> 07
    let form_field_day = $("#cur_day").text().padStart(2, '0');   // day가 10보다 작으면 앞에 0을 붙임 ex) 7 -> 07
                                                                  // type이 datetime-local 또는 date인 input태그의 value수정 시 이렇게 0이 붙은 값들을 써야 해서
    $('#id_start_date').val(cur_year + '-' + form_field_month + '-' + form_field_day);  // 시작일을 클릭한 날로
    $('#id_start_date').attr("min", cur_year + '-' + form_field_month + '-' + form_field_day); // 시작일의 최소날짜 설정
    $("#id_start_hour").val("00").prop("selected", true);         // 시작시간대를 00시로
    $("#id_start_minute").val("00").prop("selected", true);       // 시작시간대를 00분으로
    $('#id_end_date').val(cur_year + '-' + form_field_month + '-' + form_field_day);    // 종료일을 클릭한 날로
    $('#id_end_date').attr("min", cur_year + '-' + form_field_month + '-' + form_field_day); // 종료일의 최소날짜 설정
    $("#id_end_hour").val("00").prop("selected", true);           // 종료시간대를 00시로
    $("#id_end_minute").val("00").prop("selected", true);         // 종료시간대를 00분으로
    $('#id_title').val('');
    $("#id_color").val("#838de9").prop("selected", true);         // 기본컬러를 보라색으로
  });
  
  $(document).on("click", "#add-userschedule", function(){          // 모달창에서 생성버튼을 누르면 이하 내용 실행
    const start_date = document.getElementById("id_start_date").value;
    const start_hour = $("#id_start_hour option:selected").val();
    const start_minute = $("#id_start_minute option:selected").val();
    const end_date = document.getElementById("id_end_date").value;
    const end_hour = $("#id_end_hour option:selected").val();
    const end_minute = $("#id_end_minute option:selected").val();
    const title = document.getElementById("id_title").value;
    const color = document.getElementById("id_color").value;
    const csrf = document.getElementsByName('csrfmiddlewaretoken');

    const fd = new FormData();

    fd.append('csrfmiddlewaretoken', csrf[0].value);
    fd.append('start_date', start_date);
    fd.append('start_hour', start_hour);
    fd.append('start_minute', start_minute);
    fd.append('end_date', end_date);
    fd.append('end_hour', end_hour);
    fd.append('end_minute', end_minute);
    fd.append('title', title);
    fd.append('color', color);                                    // 폼에 입력한 값들을 fd라는 변수에 담아서 ajax통신
    
    $.ajax({
      url : create_userschedule_url,
      type : 'POST',
      headers : {
        'X-CSRFTOKEN' : csrf_token
      },
      data : fd,
      success:function(data){

        if(data['result'] === "success"){                   // 작성한 폼이 유효했다면 redirect
          setTimeout(function() {
            location.href = "";
          }, 300);
        }
        else{                                               // 작성한 폼이 유효 X -> 에러메시지 출력
          form_errors = JSON.parse(data['form_errors']);    // json형태의 데이터를 js객체형태로 바꿈
          
          $('#userschedule-form ul').empty();               // 오류 메시지 출력되는 부분 비우기
         
          $.each(form_errors, function(i, value){           // 2중 반복문을 돌며 오류 메시지 각 영역에 채우기
            $.each(value, function(j, message){
              let error_message = '<li>' + value[j]['message'] + '</li>';
              let error_field = i.split('_')[0]
              $("ul[id*='" + error_field +"']").append(error_message);
            });
          });
        }

      },
      error:function(){
        alert("일정을 생성하는데 실패했습니다");
      },
      cache : false,
      contentType: false,
      processData: false

    });

  });

  $(document).on("click", ".delete-schedule", function(e){             // 휴지통 아이콘 누르면 그 스케줄 삭제하기
        // e.stopPropagation();   // 부모 태그인 .content로 click이벤트가 전파되는 것을 막음
        Swal.fire({
          title: '이 일정을 삭제하시겠습니까?',
          icon: 'error',
          showCancelButton: true,
          confirmButtonColor: '#42a5f5',
          confirmButtonText: '확인',
          cancelButtonText: '취소',
        }).then((result) => {
          if(result.isConfirmed){
            let param = {
              'pk' : $(this).attr("value")
            }
    
            $.ajax({
              url : delete_userschedule_url,
              type : 'POST',
              headers : {
                'X-CSRFTOKEN' : csrf_token
              },
              data : JSON.stringify(param),
              success:function(data){
                setTimeout(function() {
                  location.href = "";
                }, 300);
                // $(self).parent().parent().remove();
      
              },
              error:function(){
                alert("일정을 삭제하는데 실패했습니다");
              }
            });
          }
    
          else{
            ;
          }
        });
      });


});


function closeSidebar() {                                           // 사이드바 닫기
  document.getElementById("Sidebar").style.right = "-35vw";
}

function go_prev_month() {                                          // 이전 달로 가기
  if (document.getElementById("Sidebar").style.right === "0px"){    // 사이드바가 보이는 상태면, 사이드바를 먼저 닫고 저번달 보여줌
    closeSidebar();
    setTimeout(function() {
      location.href = userCalendar_view_url + "?" + prev_month;
    }, 400);
  }
  else{                                                            // 사이드바가 닫힌 상태면, 바로 저번달 보여줌
    location.href = userCalendar_view_url + "?" + prev_month;
  }
}

function go_next_month() {                                          // 다음 달로 가기
  if (document.getElementById("Sidebar").style.right === "0px"){    // 사이드바가 보이는 상태면, 사이드바를 먼저 닫고 다음달 보여줌
    closeSidebar();
    setTimeout(function() {
      location.href = userCalendar_view_url + "?" + next_month;
    }, 400);
  }
  else{                                                            // 사이드바가 닫힌 상태면, 바로 다음달 보여줌
    location.href = userCalendar_view_url + "?" + next_month;
  }
}