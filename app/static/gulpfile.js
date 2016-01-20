var gulp = require('gulp');
var webpack = require('gulp-webpack');
var less = require('gulp-less');
var minify = require('gulp-minify-css');
var uglify = require('gulp-uglify');
var jshint = require('gulp-jshint');

gulp.task('default', ['auto-combine'], function () {
    console.log('default task');
});

gulp.task('less', function () {
    console.log('start pack less');
    gulp.src('./src/styles/*.less')
        .pipe(less())
        .pipe(minify())
        .pipe(gulp.dest('./dist/styles'));
});

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
});

//JS代码检查
gulp.task('jshint', function () {
    gulp.src('./src/scripts/*.js')
        .pipe(jshint())
        .pipe(jshint.reporter());
});