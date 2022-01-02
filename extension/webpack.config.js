const path = require('path')
const TerserPlugin = require('terser-webpack-plugin')
const CopyPlugin = require('copy-webpack-plugin')

module.exports = (env) => {
    let optimization = {
        minimize: true,
        minimizer: [
            new TerserPlugin({
                minify: TerserPlugin.uglifyJsMinify,
                terserOptions: {},
            }),
        ],
    }

    if (env.dev == true) {
        optimization = {}
    }

    return {
        mode: 'none',
        entry: {
            content_script: ['./src/content_scripts/main.js'],
            background: ['./src/background/main.js'],
            popup: ['./src/popup/popup.js'],
        },
        output: {
            filename: '[name].js',
            path: path.resolve(__dirname, 'dist'),
            clean: true,
        },
        optimization: optimization,
        plugins: [
            new CopyPlugin({
                patterns: [
                    {
                        from: './src/manifest.json',
                        to: 'manifest.json',
                    },
                    {
                        from: './src/popup/popup.html',
                        to: 'popup.html',
                    },
                    {
                        from: './src/popup/popup.css',
                        to: 'popup.css',
                    },
                    {
                        from: './src/icons/*',
                        to: 'icons/[name][ext]',
                    },
                ],
            }),
        ],
    }
}
