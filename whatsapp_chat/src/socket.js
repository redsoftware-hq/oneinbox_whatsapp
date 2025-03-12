import { io } from 'socket.io-client'
import { socketio_port } from '../../../../sites/common_site_config.json'


export function initSocket() {  
  let host = window.location.hostname
  let siteName = import.meta.env.VITE_SITE_NAME || window.site_name || window.location.host
  let port = window.location.port ? `:${socketio_port}` : ''
  let protocol = port ? 'http' : 'https'
  let url = `${protocol}://${host}${port}/${siteName}`
  
  console.log("Socket URL:", url)
  
  let socket = io(url, {
    withCredentials: true,
    reconnectionAttempts: 5,
  })

  return socket
}
