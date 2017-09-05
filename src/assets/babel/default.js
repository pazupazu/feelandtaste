/**
 * 実行JS
 */

// require
global.$ = global.jQuery = require("jquery");

import fullpage from 'fullpage.js/dist/jquery.fullpage.min.js'
import objectFitImages from 'object-fit-images'
// import innerHeight  from 'ios-inner-height'

$(document).ready(function() {
  //page top
  $('.btn-top').on("click", function() {
    $('body,html').animate({
      scrollTop: 0
    }, 500);
  });

  //バーガーメニュー 開閉
  $(".js-hook-menu , .gloval-nav__item").on("click", function() {
    $(".btn-burger__icon").toggleClass("btn-burger__icon--close");
    $(".gloval-nav").toggleClass("gloval-nav--open");
    $(".header").toggleClass("open");
  });

  var headH = $(".header .header__inner").height();
  var heroH = 200;

  $(window).on('scroll resize', function() {

    var distance = $(window).scrollTop();
    var headViewArea = heroH - headH;

    if (distance > headViewArea) {
      $('.header .logo, .header .btn-group').fadeOut();
    } else {
      $('.header .logo, .header .btn-group').fadeIn();
    }
  });

  // object-fit ie polifily
  // https://github.com/bfred-it/object-fit-images
  // https://www.webcreatorbox.com/tech/object-fit
  var fullImage = document.querySelectorAll('img.full-image');
  objectFitImages(fullImage);
});

// fullpage.js
$(document).ready(function() {
  $('#fullpage').fullpage({
    anchors:[
      'section1',
      'section2',
      'section3',
      'section4',
      'section5',
      'section6',
      'section7',
      'section8', 
      'section9', 
      'section10', 
      'section11',
      'section12'
    ],
    scrollBar: false,
    scrollOverflow: true, //高さがvh以上だった場合スクロールさせる
    onLeave: function(index, nextIndex, direction){
      var loadedSection = $(this);
      // section1以外ではburgermenuを上につける
      if(nextIndex >= 2){
        $('.btn-burger').addClass('btn-burger--top');
      } else {
        $('.btn-burger').removeClass('btn-burger--top');
      }
    }
  });
});

// safari ランドスケープ リサイズ
var height = window.innerHeight;

$(window).on('load resize', function () {
  responsive();
});

function responsive() {
  var w = $(window).width();
  if ( w <= 768) {
    $.fn.fullpage.destroy('all');
    
    // destroyするとページ内リンクができない data-anchorタグが挿入されない
    $('.index .section').each(function(index){
      let i = index +1;
      $(this).attr('id', 'section' + i);
    });
  } else {
    $('.index .section').css('height', height + 'px');
    if(window.innerHeight != height) {
      height = window.innerHeight;
      $('.index .section').css('height', height + 'px');
    }
  }
}

$(document).ready(function() {
  // ページ内リンク
  // 動的idに対してのイベントなので第二引数にターゲットを入れる
  $(document).on('click', '.gloval-nav__item', function() {
    var targetY = $(this.hash).offset().top;
    $("html,body").animate({scrollTop: targetY}, 600);
    return false;
  });
});