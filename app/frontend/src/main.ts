import { createApp } from 'vue'
import App from './App.vue'
import './index.css'

/* import the fontawesome core */
import {dom, library} from '@fortawesome/fontawesome-svg-core'

/* import font awesome icon component */
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

/* import specific icons */
import { fas } from '@fortawesome/free-solid-svg-icons'

library.add(fas)
dom.watch()

createApp(App)
    .component('font-awesome-icon', FontAwesomeIcon)
    .mount('#app')
