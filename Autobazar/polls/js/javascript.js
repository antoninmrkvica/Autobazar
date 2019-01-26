/**
 * Created by Antonín Mrkvica on 08.01.2019.
 */
$(document).ready(function () {
    $('.sidenav').sidenav();
    $('.collapsible').collapsible();
    $('.slider').slider();
    $('.fixed-action-btn').floatingActionButton();
});

function rotate(){
    counter +=2;
$('.rotateimg').css(
    {
        "transform": "rotate("+counter+"deg)"
    }
);
setTimeout(rotate, time)
}

let counter = 0;
let time= 10;
setTimeout(rotate, time);