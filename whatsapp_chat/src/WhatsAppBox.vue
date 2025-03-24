<template>
  <div
    v-if="reply?.message"
    class="flex items-center justify-around gap-2 px-3 pt-2 sm:px-10"
  >
    <div
      class="mb-1 ml-13 flex-1 cursor-pointer rounded border-0 border-l-4 border-green-500 bg-gray-100 p-2 text-base text-gray-600"
      :class="reply.type == 'Incoming' ? 'border-green-500' : 'border-blue-400'"
    >
      <div
        class="mb-1 text-sm font-bold"
        :class="reply.type == 'Incoming' ? 'text-green-500' : 'text-blue-400'"
      >
        {{ reply.from_name || __('You') }}
      </div>
      <div class="max-h-12 overflow-hidden" v-html="reply.message" />
    </div>

    <Button variant="ghost" icon="x" @click="reply = {}" />
  </div>
  <div class="flex items-end gap-2 px-3 py-2.5 sm:px-10 bg-gray-200" v-bind="$attrs">
    <div class="flex h-8 items-center gap-2">
      <FileUploader @success="(file) => uploadFile(file)">
        <template v-slot="{ openFileSelector }">
          <div class="flex items-center space-x-2">
            <Dropdown :options="uploadOptions(openFileSelector)">
              <FeatherIcon
                name="plus"
                class="size-4.5 cursor-pointer text-gray-600"
              />
            </Dropdown>
          </div>
        </template>
      </FileUploader>
      <IconPicker
        v-model="emoji"
        v-slot="{ togglePopover }"
        @update:modelValue="
          () => {
            content += emoji
            $refs.textareaRef.el.focus()
          }
        "
      >
        <SmileIcon
          @click="togglePopover"
          class="flex size-4.5 cursor-pointer rounded-sm text-xl leading-none text-gray-500"
        />
      </IconPicker>
    </div>
    <Textarea
      ref="textareaRef"
      type="textarea"
      class="min-h-8 w-full"
      :rows="rows"
      v-model="content"
      :placeholder="placeholder"
      @focus="rows = 6"
      @blur="rows = 1"
      @keydown.enter.stop="(e) => sendTextMessage(e)"
    />
  </div>
</template>

<script setup>
import IconPicker from './components/IconPicker.vue'
import SmileIcon from './components/Icons/SmileIcon.vue'
// import {createResource} from '@frappe-ui/resources/index.js'
import { createResource, Textarea, FileUploader, Dropdown } from 'frappe-ui'
import { ref, nextTick, watch, defineModel, onMounted } from 'vue'
import { emitter } from './utils/eventBus';
const csrfToken = window.csrf_token || window.frappe.csrf_token || frappe.csrf_token;



// Define the translation function
// const __ = (text) => text;

const props = defineProps({
  doctype: String,
  docname: String,
  phone: String,
})

const doc = defineModel('doc')
const whatsapp = defineModel('whatsapp')
const reply = defineModel('reply')
const rows = ref(1)
const textareaRef = ref(null)
const emoji = ref('')

const content = ref('')
const placeholder = ref(__('Type your message here.....'))
const fileType = ref('')

function show() {
  nextTick(() => textareaRef.value.el.focus())
}

function uploadFile(file) {
  whatsapp.value.attach = file.file_url
  whatsapp.value.content_type = fileType.value
  sendWhatsAppMessage()
}

function sendTextMessage(event) {
  if (event.shiftKey) return
  sendWhatsAppMessage()
  textareaRef.value.el?.blur()
  content.value = ''
}

async function sendWhatsAppMessage() {
 
  let args = {
    message: content.value,
    to: props.phone || doc.value.contact_number.replace(/\D/g, ""),
    attach: whatsapp?.value?.attach || '',
    reply_to: reply?.value?.name || '',
    content_type: whatsapp?.value?.content_type,
  };

  if (content) content.value = '';
  if (fileType) fileType.value = '';
  if (whatsapp.value) {
    whatsapp.value.attach = '';
    whatsapp.value.content_type = 'text';
  }
  if (reply) reply.value = {};

  createResource({
    url: 'frappe_whatsapp.api.whatsapp.create_whatsapp_message',
    params: args,
    auto: true,
    headers: {
      'X-Frappe-CSRF-Token': csrfToken
    }
  });
  
  emitter.emit("message_sent",args)

}


function uploadOptions(openFileSelector) {
  return [
    {
      label: __('Upload Document'),
      icon: 'file',
      onClick: () => {
        fileType.value = 'document'
        openFileSelector()
      },
    },
    {
      label: __('Upload Image'),
      icon: 'image',
      onClick: () => {
        fileType.value = 'image'
        openFileSelector('image/*')
      },
    },
    {
      label: __('Upload Video'),
      icon: 'video',
      onClick: () => {
        fileType.value = 'video'
        openFileSelector('video/*')
      },
    },
  ]
}

onMounted(() => {
  console.log("Initial reply:", reply.value);
}); 

watch(reply, (value) => {
  if (value?.message) {
    console.log(reply)
    show()
  }
})

defineExpose({ show })
</script>