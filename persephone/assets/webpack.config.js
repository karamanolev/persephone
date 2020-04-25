const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
    plugins: [
        new MiniCssExtractPlugin(),
    ],
    mode: 'development',
    devtool: 'source-map',
    entry: [
        '@babel/polyfill',
        path.resolve(__dirname, 'main.js'),
    ],
    output: {
        path: path.resolve(__dirname, '..', 'static', 'dist'),
        filename: 'main.js',
    },
    devServer: {
        index: '',
        port: 8101,
        publicPath: '/static/dist',
        proxy: {
            '!/static/dist/**/*': 'http://localhost:8100',
        },
    },
    resolve: {
        modules: [
            path.resolve(__dirname, 'node_modules'),
            path.resolve(__dirname),
        ],
    },
    module: {
        rules: [
            {
                test: /.jsx?$/,
                exclude: /node_modules/,
                use: [{
                    loader: 'babel-loader',
                    options: {
                        presets: [
                            '@babel/preset-env',
                            '@babel/preset-react',
                        ],
                        plugins: [],
                    },
                }],
            },
            {
                test: /\.scss$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    {
                        loader: 'css-loader',
                        options: {
                            sourceMap: true,
                        },
                    },
                    'resolve-url-loader',
                    'sass-loader',
                ],
            },
            {
                test: /\.(woff2?|ttf|otf|eot|svg|png|jpe?g|gif)$/,
                loader: 'file-loader',
                options: {
                    name: '[path][name].[ext]',
                    publicPath: '/static/dist',
                },
            },
        ],
    },
};
