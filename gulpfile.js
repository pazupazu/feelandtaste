var gulp = require("gulp");
var plumber = require('gulp-plumber');
var sourcemaps = require('gulp-sourcemaps');
var rename = require('gulp-rename');
var chmod = require('gulp-chmod');

var paths = {
    babel : "./src/assets/babel/",
    js : "./dist/assets/js/",
    scss : "./src/assets/scss/",
    css : "./dist/assets/css/",
    ejs : "./src/ejs/",
    imgSrc : './src/assets/image/',
    imgDist : './dist/assets/image/',
}


var error = function(err) {
    console.log(err.message);
}

// ejs
var ejs = require('gulp-ejs');
gulp.task("ejs", function() {
    gulp.src(
        [paths.ejs + "**/*.ejs", '!' + paths.ejs + "**/_*.ejs", '!' + paths.ejs + "contact/*.ejs"]
    )
    .pipe(plumber())
    .pipe(ejs())
    .pipe(ejs({}, {}, {"ext": ".html"}))
    .pipe(gulp.dest("./dist"))
    .pipe(browserSync.stream());
});


// プラグインの読み込み
var sass = require("gulp-sass");
var rsass = require('gulp-ruby-sass');
var sourcemaps = require('gulp-sourcemaps');
var pleeease = require('gulp-pleeease');
var clean = require('gulp-clean-css');
var sassGlob = require("gulp-sass-glob");

// Sassコンパイルタスクの定義
gulp.task("scss", function() {
  return gulp.src(paths.scss + '**/*.scss')
    .pipe(plumber({errorHandler: error}))

    .pipe(sourcemaps.init())
    .pipe(sassGlob()) 
    .pipe(sass({outputStyle: 'expanded'}).on('error', sass.logError))

    .pipe(pleeease({ //最終的に対象バージョンに合わせて出力
        autoprefixer: {"browsers": ["last 4 versions"]},
        minifier: false,
        mqpacker: true
    }))

    .pipe(sourcemaps.write('../maps'))
    .pipe(chmod(755))
    .pipe(gulp.dest(paths.css))
    .pipe(browserSync.stream());
});



// JS
var babelify = require('babelify');
var watchify = require('gulp-watchify');
var streamify = require('gulp-streamify')
var uglify = require('gulp-uglify');
var esdoc = require("gulp-esdoc");

gulp.task('js', watchify(function(watchify) {
    return gulp.src(paths.babel + '*.js')
    .pipe(plumber({errorHandler: error}))
    .pipe(sourcemaps.init())
    .pipe(watchify({
        watch: true,
        setup: function(bundle) {
            bundle.transform(babelify, {presets: "es2015"})
        }
    }))
    .pipe(streamify(uglify()))
    .pipe(streamify(sourcemaps.write()))
    .pipe(chmod(755))
    .pipe(gulp.dest(paths.js))
}))

// 画像圧縮
var imagemin = require('gulp-imagemin');
var pngquant = require('imagemin-pngquant');

gulp.task("imagemin", function(){
    var image_src = paths.imgSrc + '/**/*.+(jpg|gif|svg|png)';
    gulp.src( image_src )
    .pipe(imagemin(
        [pngquant({quality: '65-80', speed: 1})]
    ))
    .pipe(imagemin())
    .pipe(gulp.dest( paths.imgDist ));
});

// Static Server + watching scss/html files
var browserSync = require('browser-sync').create();
gulp.task('server', function() {
    browserSync.init({
        server: {
            baseDir: "./dist",
            startPath: './dist/index.html'
        }
    });
});

// COMMON
gulp.task('watch', function(){
    gulp.watch(paths.scss + '**/*.scss', ['scss']);
    gulp.watch(paths.ejs + '**/*.ejs', ['ejs']);
    gulp.watch('.dist/**/*.html').on('change', function() {
      browserSync.reload()
    });
});

gulp.task('default', ['js', 'watch', 'server']);
// gulp.task('default', ['js', 'watch', 'server']);