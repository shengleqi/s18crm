/**
 * Created by wupeiqi on 2018/1/26.
 */
$(function () {
    $('.menu .item .title').click(function () {
        $(this).next().toggleClass('hide');
    })
});