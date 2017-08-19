/**
 * 実行JS
 */

// require
global.$ = global.jQuery = require("jquery");

// fullpage
 import fullpage from 'fullpage.js/dist/jquery.fullpage.min.js'

 $(document).ready(function() {
  //page top
  $('.btn-top').on("click", function() {
    console.log('OK');
    $('body,html').animate({
      scrollTop: 0
    }, 500);
    return false;
  });

  //バーガーメニュー 開閉
  $(".js-hook-menu").on("click", function() {
    $(".btn-burger__icon").toggleClass("btn-burger__icon--close");
    $(".gloval-nav").toggleClass("gloval-nav--open");
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
});

$(document).ready(function() {
  $('#fullpage').fullpage({
    onLeave: function(index, nextIndex, direction){
      var loadedSection = $(this);
      if(nextIndex >= 2){
        $(".btn-burger").addClass("btn-burger--top");
      } else {
        $(".btn-burger").removeClass("btn-burger--top");
      }
    }
  });
});