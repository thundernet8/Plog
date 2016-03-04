"use strict";

var $ = require('jquery');

var siteUrl = window.location.protocol + '//' + window.location.host,
    uploadApiUrl = siteUrl + '/api/v1.0/uploads';

//图片等文件上传

$(function () {
   $('input[type="file"]').on('change', function (e) {
       //e.preventDefault();
       console.log($(this).files);
       var data = new FormData();
       $.each($(this).files, function (i, file) {
          data.append('upload_file', file);
       });
       $.ajax({
           url: uploadApiUrl,
           type: 'post',
           data: data,
           cache: false,
           contentType: false,
           processData: false,
           success: function(data){
               console.log(data); // TODO
           }
       })
   })
});