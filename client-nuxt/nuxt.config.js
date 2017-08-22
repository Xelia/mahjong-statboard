module.exports = {
  /*
  ** Headers of the page
  */
  head: {
    title: 'Rating',
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: 'Nuxt.js project' }
    ],
    link: [
      { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
    ]
  },
  /*
  ** Customize the progress-bar color
  */
  loading: { color: '#3B8070' },
  /*
  ** Build configuration
  */
  build: {
    /*
    ** Run ESLINT on save
    */
    // extend (config, ctx) {
    //   if (ctx.isClient) {
    //     config.module.rules.push({
    //       enforce: 'pre',
    //       test: /\.(js|vue)$/,
    //       loader: 'eslint-loader',
    //       exclude: /(node_modules)/
    //     })
    //   }
    // }
  },
  modules:[
    '@nuxtjs/proxy',
    ['@nuxtjs/axios',
      {
        baseURL: "http://localhost:3000/api",
        debug: true,
      }
    ]
  ],
  mode: 'spa',
  plugins: [
    '~plugins/buefy'
  ],
  css: [
    { src: 'font-awesome/css/font-awesome.css', lang: 'css' },
  ],
  proxy: {
    '/api': {target: 'http://localhost:8000/', pathRewrite:{'/api': ''}},
    '/admin': {target: 'http://localhost:8000/'},
    '/static': {target: 'http://localhost:8000/'}
  },
  router: {
    middleware: 'check-auth'
  },
}
