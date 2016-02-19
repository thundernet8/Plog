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
        login: './src/scripts/page-login.js',
        register: './src/scripts/page-register.js',
        home: './src/scripts/page-home.js',
        article: './src/scripts/page-article.js'
    },

    output: {
        //filename : '[hash].[name].js'
        filename : 'page-[name].js'
    },

    externals: {
        'jquery': 'jQuery'
    }
}