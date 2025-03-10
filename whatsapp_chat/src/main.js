import { createApp } from 'vue'
import App from './App.vue'
import { initSocket } from './socket'
import './index.css'

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

for (let key in globalComponents) {
  app.component(key, globalComponents[key])
}

// Initialize WebSocket
let socket

// Helper function to log and mount app
const mountApp = () => {
  socket = initSocket()
  app.config.globalProperties.$socket = socket
  console.log('Socket initialized:', socket)
  app.mount('#app')
  console.log('App mounted successfully.')
}

console.log('Running in development mode...')

frappeRequest({ url: '/api/method/frappe_whatsapp.www.whatsapp_chat.get_context_for_dev' })
  .then((values) => {
    console.log('Response from get_context_for_dev:', values)

    if (!values) {
      console.error('No response received from API')
      return
    }

    // Assign response values to window object
    for (let key in values) {
      window[key] = values[key]
    }

    mountApp()
  })
  .catch((error) => {
    console.error('Error fetching get_context_for_dev:', error)
  })
