import { createApp } from 'vue'
import App from './App.vue'
import { initSocket } from './socket'
import './index.css'
import { createRouter, createWebHistory } from 'vue-router'
import {
  FrappeUI,
  Button,
  Input,
  TextInput,
  FormControl,
  ErrorMessage,
  Dialog,
  Alert,
  Badge,
  setConfig,
  frappeRequest,
  FeatherIcon,
} from 'frappe-ui'

// Register global components
let globalComponents = {
  Button,
  TextInput,
  Input,
  FormControl,
  ErrorMessage,
  Dialog,
  Alert,
  Badge,
  FeatherIcon,
}

// Create Vue app instance
let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)
app.use(FrappeUI)



// Register global components
for (let key in globalComponents) {
  app.component(key, globalComponents[key])
}

let socket

const mountApp = () => {
  socket = initSocket()
  app.config.globalProperties.$socket = socket
  app.mount('#app')
  console.log('App mounted successfully.')
}

  if (import.meta.env.DEV) {
    frappeRequest({ 
      url: '/api/method/frappe_whatsapp.www.whatsapp_chat.get_context_for_dev',
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      }
    }).then(
      (values) => {
        if (!window.frappe) {
          window.frappe = {}; 
        }
        
        for (let key in values) {
          window.frappe[key] = values[key];
        }        
        socket = initSocket()
        app.config.globalProperties.$socket = socket
        app.mount('#app')
      },
    )
  } else {
    socket = initSocket()
    app.config.globalProperties.$socket = socket
    app.mount('#app')
  }
  