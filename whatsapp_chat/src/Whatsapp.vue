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

// const contacts = ref([]);
const selectedPhone = ref(null);
const showWhatsappTemplates = ref(false);
const showAddLeadModal = ref(false);
const isLoading = ref(false);
const user_update = ref(false);
// const whatsappMessages = ref([]);

// const fetchContacts = async () => {
//   try {
    // const response = await fetch("/api/method/frappe_whatsapp.api.whatsapp.get_whatsapp_contact");
const WhatsappContacts = createResource({
      url: "/api/method/frappe_whatsapp.api.whatsapp.get_whatsapp_contact",
      auto: true,
    })
    // .fetch().then((res) => {
    //   contacts.value = res 
    //   console.log("Contacts fetched:", contacts.value);
    // })
    // const data = response
    // contacts.value = response
  // } catch (error) {
    // console.error("Error fetching contacts:", error);
  // }
// };

// async function sendMessageOnContactClick(phone) {
//   if (!phone) return;

//   try {
//     const response = await createResource({
//       url: "/api/method/frappe_whatsapp.api.whatsapp.send_message",
//       params: { phone, message: "Hello! How can I assist you today?" },
//       auto: false,
//     }).fetch();
//     console.log("Message sent successfully!", response);
//   } catch (error) {
//     console.error("Error sending message:", error);
//   }
// }

// async function resetMessageCount(phone) {
//   if (!phone) return;

//   try {
//     await createResource({
//       url: "/api/method/frappe_whatsapp.api.whatsapp.reset_unread_count",
//       params: { phone },
//       auto: false,
//     }).fetch();
//     console.log("Message count reset successfully for", phone);
//   } catch (error) {
//     console.error("Error resetting message count:", error);
//   }
// }

// watch(selectedPhone, async (newPhone) => {
//   if (!newPhone) return;
  
//   try {
//     const response = await createResource({
//       url: '/api/method/frappe_whatsapp.api.whatsapp.get_whatsapp_messages',
//       params: { phone: newPhone.number },
//       auto: false,
//     }).fetch();

//     whatsappMessages.value = response.sort((a, b) => new Date(a.creation) - new Date(b.creation));
//     console.log("Received messages:", whatsappMessages.value);
//     resetMessageCount(newPhone.number);
//     scrollToBottom();
//   } catch (error) {
//     console.error("Error fetching messages:", error);
//   }
// });

const whatsappMessages = createResource({
  url: 'frappe_hfhg.api.whatsapp.get_whatsapp_messages',
  cache: ['whatsapp_messages', props.phone],
  params: {
    // reference_doctype: props.doctype,
    // reference_name: props.docname,
    phone: selectedPhone.value
  },
  auto: true,
  // headers: {
  //   'X-Frappe-CSRF-Token': frappe.csrf_token
  // },
  transform: (data) => data.sort((a, b) => new Date(a.creation) - new Date(b.creation)),
});

function sendTemplate(template) {
  showWhatsappTemplates.value = false;
  try {
    createResource({
      url: 'frappe_whatsapp.api.whatsapp.send_whatsapp_template',
      params: {
        reference_doctype: props.doctype,
        reference_name: props.docname,
        to: props.phone,
        template,
      },
      auto: true,
    }).then(() => {
      console.log('Template sent successfully!');
    });
  } catch (error) {
    console.error('Error sending template:', error);
  }
}

// function fetchMessages() {
//   if (!selectedPhone.value) return;
//   createResource({
//     url: '/api/method/frappe_whatsapp.api.whatsapp.get_whatsapp_messages',
//     params: { phone: selectedPhone.value.number },
//     auto: true,
//   }).fetch().then((response) => {
//     whatsappMessages.value = response.sort((a, b) => new Date(a.creation) - new Date(b.creation));
//     console.log("Received messages:", whatsappMessages.value);
//     scrollToBottom();
//   }).catch((error) => {
//     console.error("Error fetching messages:", error);
//   });
// }

function scrollToBottom() {
  nextTick(() => {
    const el = document.querySelector('.messages-container');
    if (el) el.scrollTop = el.scrollHeight;
  });
}

watch(whatsappMessages.data, () => {
  nextTick(scrollToBottom);
});

onMounted(() => {
  // fetchContacts();

  $socket.on('oneinbox_whatsapp_message', (data) => {
    if (selectedPhone.value && selectedPhone.value.number === data.from || data.to) {
      // whatsappMessages.value.push(data);
      // whatsappMessages.value.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
      whatsappMessages.reload()
      // nextTick(scrollToBottom);
    }
  });
  $socket.on('lead_submission_completed', () => {
    // fetchContacts()
    WhatsappContacts.reload()
  });
  $socket.on('whatsapp_contact_update', () => {
    user_update.value = true;
    WhatsappContacts.reload()
    // fetchContacts();
  });

  emitter.on('contact-selected', (data) => {
    console.log("Contact selected:", data);
    if (!selectedPhone.value || selectedPhone.value.number !== data.number) {
      selectedPhone.value = data;
    }
  });

  emitter.on("lead_submission_started", () => {
    isLoading.value = true;
  });

  emitter.on("lead_submission_completed", () => {
    isLoading.value = false;
    showAddLeadModal.value = false;
  });
});

onBeforeUnmount(() => {
  console.log("Component is being unmounted, removing event listeners.");
  $socket.off('oneinbox_whatsapp_message');
  $socket.off('whatsapp_contact_update');
});
</script>

<template>
  <div class="flex h-4/5 flex-col scroll " :class="{ 'splash-screen': isLoading }">
    <div class="top-bar flex p-3 bg-white">
      <div class="flex column gap-5 w-full">
         <a href="/app" class="text-2xl">←</a>
        <div class="flex gap-2 items-center">
          <WhatsAppIcon class="h-8 w-8 text-gray-500" />
          <h1>Whatsapp</h1>
        </div>
      </div>
    </div>

    <div class="flex h-screen overflow-hidden">
      <div class="w-1/5">
        <WhatsappSidebar :contacts="WhatsappContacts.data" :user_update="user_update" :socket="$socket" />
      </div>

      <div class="whatsapp-chat-container h-screen w-full flex-col">
        <div class="top-bar flex items-center justify-between p-2 bg-white" v-if="selectedPhone">
          <div class="flex flex-col">
            <h2 class="text-xl font-semibold text-gray-800">{{ selectedPhone?.number || "" }}</h2>
            <h2 class="text-sm font-semibold text-gray-800">{{ selectedPhone?.name || '' }}</h2>
          </div>
          <div class="flex items-center space-x-4">
            <Button @click="showAddLeadModal = true" class="bg-gray-700 text-black" :showAddLeadModal="showAddLeadModal">+ Add Lead</Button>
            <Button @click="showWhatsappTemplates = true">Send Template</Button>
          </div>
        </div>

        <div v-if="!selectedPhone" class="flex flex-1 flex-col items-center justify-center gap-3 text-xl font-medium text-gray-500">
          <span>Click Any Contact To View Conversation</span>
        </div>

        <div v-else-if="selectedPhone && !whatsappMessages.data?.length" class="flex flex-1 flex-col items-center justify-center gap-3 text-xl font-medium text-gray-500">
          <WhatsAppIcon class="h-10 w-10 text-gray-500" />
          <span>No messages yet</span>
        </div>

        <div v-else class="messages-container flex-1 p-4 overflow-y-auto">
          <WhatsAppArea class="px-3 sm:px-10" :messages="whatsappMessages.data" />
        </div>

        <div class="chat-box-container border-t-gray-100 mb-16">
          <WhatsAppBox v-if="selectedPhone"
            :doctype="props.doctype"
            :docname="props.docname"
            :phone="selectedPhone?.number"
            @message-sent="whatsappMessages.reload"
          />
        </div>

        <WhatsappTemplateSelectorModal v-model="showWhatsappTemplates" :doctype="doctype" @send="(t) => sendTemplate(t)"/>
        <WhatappAddToLeadModal
          v-model="showAddLeadModal"
          :first_name="selectedPhone?.name || ''"
          :contact_number="selectedPhone?.number || ''"
          :isLoading="isLoading"/>
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