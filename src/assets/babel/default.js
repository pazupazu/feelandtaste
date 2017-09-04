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

// width 769以上でのみ発火させる
$(document).ready(function() {
  var w = $(window).width();
  if ( w >= 769) {
    page();
  } else {
    // // グロナビのターゲットを書き換え
    // $('.gloval-nav__inner .item--top').replaceWith('<a href="index.html#sectionTop" class="gloval-nav__item"><span>TOP</span></a>');
    // $('.gloval-nav__inner .item--story').replaceWith('<a href="index.html#sectionStory" class="gloval-nav__item"><span>STORY</span></a>');
    // $('.gloval-nav__inner .item--new-collection').replaceWith('<a href="index.html#sectionNewCollection" class="gloval-nav__item"><span>NEW COLLECTION</span></a>');
    // $('.gloval-nav__inner .item--archives').replaceWith('<a href="index.html#sectionArchives" class="gloval-nav__item"><span>ARCHIVES</span></a>');
    // $('.gloval-nav__inner .item--about').replaceWith('<a href="index.html#sectionAbout"class="gloval-nav__item"><span>ABOUT</span></a>');

    // $('.gloval-nav__item').click(function() {
    //   var speed = 600;
    //   var href= $(this).attr("href");
    //   var target = $(href == "#" || href == "" ? 'html' : href);
    //   var position = target.offset().top;
    //   $('.btn-burger').addClass('btn-burger--top');
    //   $(".header").removeClass("open");
    //   $('body,html').animate({scrollTop:position}, speed, 'swing');
      
    //   return false;
    // });
  }
});

// fullapge.js自体をラップ
function page() {
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
}

// safari ランドスケープ リサイズ
var height = window.innerHeight;

$(window).on('load resize', function () {
  responsive();
});

function responsive() {
  var w = $(window).width();
  if ( w >= 769) {
    $('.index .section').css('height', height + 'px');
    if(window.innerHeight != height) {
      height = window.innerHeight;
      $('.index .section').css('height', height + 'px');
    }
  }
}
