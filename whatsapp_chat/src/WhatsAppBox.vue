<template>
  <!-- Iterate through replies and add separation based on date -->
  <div
    v-for="(message, index) in replies"
    :key="index"
    class="flex items-center justify-around gap-2 px-3 pt-2 sm:px-10"
  >
    <!-- If the current message's date is different from the previous one, add a separator -->
    <div v-if="shouldShowSeparator(index)" class="w-full text-center">
      <div class="separator font-semibold text-gray-500">
        {{ formatDate(message.creation) }}
      </div>
      <div class="border-t border-gray-300 my-2"></div> <!-- Separator -->
    </div>

    <!-- Message Content -->
    <div
      v-if="message?.message"
      class="mb-1 ml-13 flex-1 cursor-pointer rounded border-l-4 p-2"
      :class="message.type == 'Incoming' ? 'border-green-500' : 'border-blue-400'"
    >
      <div
        class="mb-1 text-sm font-bold"
        :class="message.type == 'Incoming' ? 'text-green-500' : 'text-blue-400'"
      >
        {{ message.from_name || __('You') }}
      </div>
      <div class="max-h-12 overflow-hidden" v-html="message.message"></div>
    </div>

    <Button variant="ghost" icon="x" @click="reply = {}" />
  </div>

  <!-- Input Section -->
  <div class="flex items-end gap-2 px-3 py-2.5 sm:px-10" v-bind="$attrs">
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
import { format, isToday, isYesterday } from 'date-fns';
import IconPicker from './components/IconPicker.vue';
import SmileIcon from './components/Icons/SmileIcon.vue';
import { createResource, Textarea, FileUploader, Dropdown } from 'frappe-ui';
import { ref, nextTick, watch, defineModel } from 'vue';

// Define properties and refs
const props = defineProps({
  doctype: String,
  docname: String,
  phone: String,
  reply: Object,
});

const doc = defineModel('doc');
const whatsapp = defineModel('whatsapp', { default: () => ({ attach: '', content_type: 'text' }) });
const reply = defineModel('reply');
const rows = ref(1);
const textareaRef = ref(null);
const emoji = ref('');

const content = ref('');
const placeholder = ref(__('Type your message here...'));
const fileType = ref('');

// Watcher for reply updates
watch(reply, (value) => {
  if (value?.message) {
    show();
  }
});

defineExpose({ show });

// Function to show text area
function show() {
  nextTick(() => textareaRef.value.el.focus());
}

// Upload file handler
function uploadFile(file) {
  whatsapp.value.attach = file.file_url;
  whatsapp.value.content_type = fileType.value;
  sendWhatsAppMessage();
}

// Send text message handler
function sendTextMessage(event) {
  if (event.shiftKey) return; // Allow Shift + Enter for new lines
  event.preventDefault(); // Prevent unintended form submission

  sendWhatsAppMessage();
  textareaRef.value.el?.blur();
  content.value = '';
}

// Send WhatsApp message
async function sendWhatsAppMessage() {
  console.log("Sending WhatsApp message...", props);
  console.log("Content:", content.value);

  let args = {
    message: content.value,
    to: props.phone || (doc.value?.phone ? doc.value.contact_number.replace(/\D/g, '') : ''),
    attach: whatsapp.value?.attach || '',
    reply_to: reply.value?.name || '',
    content_type: whatsapp.value?.content_type || 'text',
  };

  createResource({
    url: '/api/method/frappe_whatsapp.api.whatsapp.create_whatsapp_message',
    params: args,
    auto: true,
    headers: {},
  }).fetch().then((response) => {
    console.log('Message sent successfully!', response);
  }).catch((error) => {
    console.error('Error sending message:', error);
  });
}

// Upload options for file type selection
function uploadOptions(openFileSelector) {
  return [
    {
      label: __('Upload Document'),
      icon: 'file',
      onClick: () => {
        fileType.value = 'document';
        openFileSelector();
      },
    },
    {
      label: __('Upload Image'),
      icon: 'image',
      onClick: () => {
        fileType.value = 'image';
        openFileSelector('image/*');
      },
    },
    {
      label: __('Upload Video'),
      icon: 'video',
      onClick: () => {
        fileType.value = 'video';
        openFileSelector('video/*');
      },
    },
  ];
}

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return '';
  const lastInteraction = new Date(dateString);
  let formattedTime = '';
  const currentYear = new Date().getFullYear();
  const messageYear = lastInteraction.getFullYear();

  if (isToday(lastInteraction)) {
    formattedTime = format(lastInteraction, 'hh:mm a');
  } else if (isYesterday(lastInteraction)) {
    formattedTime = 'Yesterday';
  } else if (currentYear === messageYear) {
    formattedTime = format(lastInteraction, 'dd MMM');
  } else {
    formattedTime = format(lastInteraction, 'dd/MM/yy');
  }
  return formattedTime;
};

// Determine whether to show separator based on message date
function shouldShowSeparator(index) {
  if (index === 0) return true; // Always show separator for the first message
  const currentMessageDate = new Date(replies[index].creation);
  const previousMessageDate = new Date(replies[index - 1].creation);
  return currentMessageDate.getDate() !== previousMessageDate.getDate(); // Show separator if different date
}
</script>
