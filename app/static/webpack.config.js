/**
 * Created by WXQ on 16/1/20.
 */

module.exports = {
    resolve: {
        root: [process.cwd() + '/src', process.cwd() + '/node_modules'],
        alias: {},
        extensions: ['', '.js', '.css', '.less', '.ejs', '.png', '.jpg']
    },

    entry: {
        index: './src/scripts/index.js',
        post_detail: './src/scripts/post-detail.js'
    },

    output: {
        filename : '[hash].[name].js'
    },
}