const gulp = require('gulp');
const gOpen = require('gulp-open');

gulp.task('default', gulp.series(reload));
gulp.task('reload', gulp.series(reload));

function reload() {
    return gulp.src(__filename).pipe(
        gOpen({ app: 'google-chrome', uri: "http://reload.extensions" })
    );
}
