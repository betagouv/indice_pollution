import Vue from 'vue'
import Search from './components/Search.vue'
import Indices from './components/Indices.vue'
import Episodes from './components/Episodes.vue'

Vue.config.productionTip = false

new Vue({
  el: '#app',
  components: {
    search: Search,
    indices: Indices,
    episodes: Episodes
  },
})