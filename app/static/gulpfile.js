var gulp = require('gulp');
var webpack = require('gulp-webpack');
var less = require('gulp-less');
var minify = require('gulp-minify-css');
var uglify = require('gulp-uglify');
var imagemin = require('gulp-imagemin');
var jshint = require('gulp-jshint');
var cache = require('gulp-cache');

gulp.task('default', ['auto-combine'], function () {
    console.log('default task');
});

//less样式压缩发布
gulp.task('less', function () {
    console.log('start pack less');
    gulp.src('./src/styles/*.less')
        .pipe(less())
        .pipe(minify())
        .pipe(gulp.dest('./dist/styles'));
});

//图片压缩发布
gulp.task('imagemin', function () {
   console.log('image minify');
    gulp.src('./src/images/**/*.{png,jpg,gif,ico}')
        .pipe(cache(imagemin({
            optimizationLevel: 5, //类型：Number  默认：3  取值范围：0-7（优化等级）
            progressive: true, //类型：Boolean 默认：false 无损压缩jpg图片
            interlaced: true, //类型：Boolean 默认：false 隔行扫描gif进行渲染
            multipass: true //类型：Boolean 默认：false 多次优化svg直到完全优化
        })))
        .pipe(gulp.dest('./dist/images'));
});

//js压缩混淆发布
gulp.task('scripts', function () {
    console.log('start pack scripts');
    gulp.src('./src/scripts/*.js')
        .pipe(webpack(require('./webpack.config.js')))
        .pipe(uglify())
        .pipe(gulp.dest('./dist/scripts'))
});

//自动合并JS,LESS 任务
gulp.task('auto-combine', function () {
    console.log('execute watch and auto-combine task');
    gulp.watch('./src/scripts/*.js', ['scripts']);
    gulp.watch('./src/styles/*.less', ['less']);
    gulp.watch('./src/images/**/*.{png,jpg,gif,ico}', ['imagemin']);
});

//JS代码检查
gulp.task('jshint', function () {
    gulp.src('./src/scripts/*.js')
        .pipe(jshint())
        .pipe(jshint.reporter());
});