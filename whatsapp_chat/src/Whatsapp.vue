<script setup>
import { getCurrentInstance, ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue';
import WhatsAppArea from './WhatsAppArea.vue';
import WhatsAppBox from './WhatsAppBox.vue';
import { createResource } from 'frappe-ui';
import WhatsAppIcon from './components/Icons/WhatsAppIcon.vue';
import WhatsappTemplateSelectorModal from './components/WhatsappTemplateSelectorModal.vue';
import WhatsappSidebar from './WhatsappSidebar.vue';
import WhatappAddToLeadModal from './components/WhatappAddToLeadModal.vue';
import { Button } from "frappe-ui";
import { emitter } from './utils/eventBus';

const app = getCurrentInstance();
const { $socket } = app.appContext.config.globalProperties;
const csrfToken = window.frappe ? window.frappe.csrf_token : '';

const props = defineProps({
  doctype: String,
  docname: String,
  phone: String,
  to: String,
  document: {
    type: Object,
    default: () => ({})
  }
});

const contacts = ref([]);
const selectedPhone = ref(null);
const showWhatsappTemplates = ref(false);
const showAddLeadModal = ref(false);
const isLoading = ref(false);
const whatsappMessages = ref([]);
const user_update = ref(false);
const isMappingSet = ref(false);

const fetchContacts = async () => {
  try {
    const response = await fetch("/api/method/frappe_whatsapp.api.whatsapp.get_whatsapp_contact", {
      headers: { 'X-Frappe-CSRF-Token': csrfToken }
    });
    const data = await response.json();
    contacts.value = data.message || [];
  } catch (error) {
    console.error("Error fetching contacts:", error);
  }
};
const resetMessageCount = async (phone) => {
      if (!phone) return;
      try {
        await fetch("/api/method/frappe_whatsapp.api.whatsapp.reset_unread_count", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Frappe-CSRF-Token": window.csrf_token || window.frappe.csrf_token,
          },
          body: JSON.stringify({ phone }),
        });
      } catch (error) {
        console.error("Error resetting message count:", error);
      }
    };


const fetchMessages = async () => {
  if (!selectedPhone.value) return;
  
  try {
     const response = await createResource({
       url: '/api/method/frappe_whatsapp.api.whatsapp.get_whatsapp_messages',
       params: { phone: selectedPhone.value.number },
       auto: false,
       headers: {
        'X-Frappe-CSRF-Token': frappe.csrf_token
      }
     }).fetch();
 
     whatsappMessages.value = response.sort((a, b) => new Date(a.creation) - new Date(b.creation));
     resetMessageCount(selectedPhone.value.number);
     scrollToBottom();
   } catch (error) {
     console.error("Error fetching messages:", error);
   }
};
async function sendTemplate(template) {
  showWhatsappTemplates.value = false;
  try {
    const response=await createResource({
      url: 'frappe_whatsapp.api.whatsapp.send_whatsapp_template',
      params: {
        to: selectedPhone.value.number,
        template,
      },
      auto: true,
      headers: {
        'X-Frappe-CSRF-Token': frappe.csrf_token
      }
    }).fetch()

    if (response)
      console.log('Template sent successfully!');
   
  } catch (error) {
    console.error('Error sending template:', error);
  }
}


onMounted(async () => {
  try {
    const response = await fetch('/api/method/frappe_whatsapp.api.whatsapp.is_mapping_set', {
      method: 'GET',
      headers: {
        'X-Frappe-CSRF-Token': window.frappe ? window.frappe.csrf_token : '',
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();
    isMappingSet.value = data.message.set_status;
  } catch (error) {
    console.error("Error fetching API:", error);
  }
  fetchContacts();
  if ($socket) {
  $socket.on('oneinbox_whatsapp_message', (data) => {
    if (
      selectedPhone.value &&
      (data.from === selectedPhone.value.number || data.to === selectedPhone.value.phone)
    ) {
      whatsappMessages.value.push(data);
      whatsappMessages.value.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
      nextTick(scrollToBottom);
    }
  });

  $socket.on('whatsapp_contact_update', async (data) => {
    await fetchContacts();

    if (selectedPhone.value && selectedPhone.value.number === data.phone) {
      return; // Avoid unnecessary updates
    }

    const existingIndex = contacts.value.findIndex((c) => c.phone === data.phone);
    
    if (existingIndex !== -1) {
      const existingContact = contacts.value[existingIndex];
      if (!data.changed_fields || data.changed_fields.length === 0) {
          return;
          }
      if (data.changed_fields.includes("last_message_time")) {
        contacts.value.splice(existingIndex, 1);
        contacts.value.unshift({ ...existingContact, ...data });
      } else if (data.changed_fields.includes("unread_message_count") ) {
        contacts.value[existingIndex] = { ...existingContact, ...data };
      }
    } else {
      contacts.value.unshift(data);
    }

    contacts.value = [...contacts.value];
     alert(selectedContact.value,data.phone)
    if (selectedContact.value === data.phone) {
      resetMessageCount(selectedContact.value);
    }
  });
}

  emitter.on('lead_submission_started', ()=>isLoading.value = true);
  emitter.on('lead_submission_process_error',alert("some error occured"));

  emitter.on('lead_submission_process_completed', ()=>{isLoading.value = false,window.location.reload()});
  emitter.on('contact-selected', (data) => {
    if (!selectedPhone.value || selectedPhone.value.number !== data.number) {
      selectedPhone.value = data;
      fetchMessages(); 
    }
  });
});

const scrollToBottom = () => {
  nextTick(() => {
    const el = document.querySelector('.messages-container');
    if (el) el.scrollTop = el.scrollHeight;
  });
};

onBeforeUnmount(() => {
  if ($socket) {
    $socket.off('oneinbox_whatsapp_message');
    $socket.off('whatsapp_contact_update');
    $socket.off('lead_submission_completed');
  }
});
</script>


<template>
  <div class="flex h-4/5 flex-col scroll  " :class="{ 'splash-screen': isLoading }">
    <div class="top-bar flex p-3 bg-white">
      <div class="flex column  w-full">
        <div class="flex column gap-5 w-full">
         <a href="/app" class="text-2xl">←</a>
        <div class="flex gap-2 items-center">
          <WhatsAppIcon class="h-8 w-8 text-gray-500" />
          <h1>Whatsapp</h1>
        </div>
      </div>
      <h1 class="w-full text-red-500" v-if="!isMappingSet">
  Lead Mapping is Not Configured Yet
</h1>


      </div>
    </div>

    <div class="flex h-screen overflow-hidden">
      <div class="w-1/5 h-screen">
        <WhatsappSidebar :contacts="contacts" :user_update="user_update" :socket="$socket" />
      </div>

      <div class="whatsapp-chat-container h-screen w-full flex-col">
        <div class="top-bar flex items-center justify-between p-2 bg-white" v-if="selectedPhone">
          <div class="flex flex-col">
            <h2 class="text-xl font-semibold text-gray-800">{{ selectedPhone?.number || "" }}</h2>
            <h2 class="text-sm font-semibold text-gray-800">{{ selectedPhone?.name || '' }}</h2>
          </div>
          <div class="flex items-center space-x-4">
            <Button @click="showAddLeadModal = true" class="bg-gray-700 text-black" :showAddLeadModal="showAddLeadModal" :disabled="!isMappingSet" >+ Add Lead</Button>
            <Button @click="showWhatsappTemplates = true" :disabled="!isMappingSet">Send Template</Button>
          </div>
        </div>

        <div v-if="!selectedPhone" class="flex flex-1 flex-col items-center justify-center gap-3 text-xl font-medium text-gray-500 bg-gray-200">
          <span>Click Any Contact To View Conversation</span>
        </div>

        <div v-else-if="selectedPhone && whatsappMessages.length === 0" class="flex flex-1 flex-col items-center justify-center gap-3 text-xl font-medium text-gray-500 bg-gray-200">
          <WhatsAppIcon class="h-10 w-10 text-gray-500" />
          <span>No messages yet</span>
        </div>

        <div v-else class="messages-container flex-1 p-4 overflow-y-auto bg-gray-200">
          <WhatsAppArea class="px-3 sm:px-10" :messages="whatsappMessages" />
        </div>

        <div class="chat-box-container border-t-gray-200 mb-16">
          <WhatsAppBox v-if="selectedPhone" :doctype="props.doctype" :docname="props.docname" :phone="selectedPhone?.number" @message-sent="fetchMessages" />
        </div>

        <WhatsappTemplateSelectorModal v-model="showWhatsappTemplates" :doctype="doctype" @send="(t) => sendTemplate(t)"/>
        <WhatappAddToLeadModal v-model="showAddLeadModal" :first_name="selectedPhone?.name || ''" :contact_number="selectedPhone?.number || ''" :isLoading="isLoading"/>
      </div>
    </div>
  </div>
</template>

<style>
.whatsapp-chat-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh);
  max-height: 100%;
  background-color: #c9cbce;
}
.splash-screen::after {
  content: "Saving Lead...";
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
  background-color: rgba(0, 0, 0, 0.7);
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 9999;
}

* {
  overflow-y: hidden;
  overflow-x: hidden;
}
</style>