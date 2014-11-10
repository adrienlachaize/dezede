function changeImage ($reader, inc) {
  var images = $reader.data('images');
  var current = $reader.data('current');
  if (typeof current == 'undefined') {
    current = -1;
  }
  current += inc;
  if (current < 0 || current >= images.length ) {
    return;
  }
  $reader.find('.reader img').attr('src', images[current]);
  $reader.data('current', current);
  if (current == 0) {
    $reader.find('.prev').addClass('disabled');
  } else {
    $reader.find('.prev').removeClass('disabled');
  }
  if (current == (images.length - 1)) {
    $reader.find('.next').addClass('disabled');
  } else {
    $reader.find('.next').removeClass('disabled');
  }
}

function createReader($reader) {
  $reader.find('.btn.zoom').off().click(function (e) {
    e.preventDefault();
    $reader.find('.reader img').click();
  });

  $reader.find('.prev').off().click(function (e) {
    e.preventDefault();
    changeImage($reader, -1);
  });
  $reader.find('.next').off().click(function (e) {
    e.preventDefault();
    changeImage($reader, 1);
  }).click();

  $reader.find('.reader img').off().click(function (e) {
    var $div = $(this).parent();

    if ($div.hasClass('zoomed')) {
      if ($(this).hasClass('dragged')) {
        $(this).removeClass('dragged');
        if ($(this).data('moved')) {
          $(this).data('moved', false);
          return;
        }
      }
      $div.removeClass('zoomed')
    } else {
      var previousWidth = $(this).width();
      var previousHeight = $(this).height();
      $div.addClass('zoomed');
      $div.scrollLeft((e.offsetX * $(this).width() / previousWidth)
                      - $div.width() / 2);
      $div.scrollTop((e.offsetY * $(this).height() / previousHeight)
                     - $div.height() / 2);
    }
    $reader.find('.btn.zoom .fa').toggleClass('fa-search-plus').toggleClass('fa-search-minus');
  }).mousedown(function (e) {
    e.preventDefault();
    var $div = $(this).parent();
    if ($div.hasClass('zoomed')) {
      $(this).data('X', $div.scrollLeft() + e.pageX);
      $(this).data('Y', $div.scrollTop() + e.pageY);
      $(this).addClass('dragged');
    }
  }).mousemove(function (e) {
    if ($(this).hasClass('dragged')) {
      $(this).data('moved', true);
      var $div = $(this).parent();
      $div.scrollLeft(parseInt($(this).data('X')) - e.pageX);
      $div.scrollTop(parseInt($(this).data('Y')) - e.pageY);
    }
  }).mouseout(function() {
    $(this).removeClass('dragged');
  }).focusout(function() {
    $(this).removeClass('dragged');
  });

  $(document).keydown(function (e) {
    if (!$reader.is(':visible')) {
      return;
    }

    if (e.keyCode == 37) {
      e.preventDefault();
      changeImage($reader, -1);
    } else if (e.keyCode == 39) {
      e.preventDefault();
      changeImage($reader, 1);
    }
  });
}
