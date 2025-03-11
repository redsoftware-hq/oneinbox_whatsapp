<template>
  <div>
    <div v-for="(group, date) in groupedMessages" :key="date">
      <!-- Date Header -->
      <div class="text-center text-gray-500 text-sm py-2">
        {{ date }}
      </div>

      <!-- Messages under this date -->
      <div
        v-for="whatsapp in group"
        :key="whatsapp.name"
        class="activity group flex gap-2"
        :class="[
          whatsapp.type == 'Outgoing' ? 'flex-row-reverse' : '',
          whatsapp.reaction ? 'mb-7' : 'mb-3',
        ]"
      >
        <div
          :id="whatsapp.name"
          class="group/message relative max-w-[90%] rounded-md bg-gray-50 p-1.5 pl-2 text-base shadow-sm"
        >
          <div v-html="formatWhatsAppMessage(whatsapp.message)" />
          <div class="text-xs text-gray-600">
            {{ dateFormat(whatsapp.creation, 'hh:mm a') }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { dateFormat } from './utils';
import { format, isToday, isYesterday } from "date-fns";


const props = defineProps({
  messages: Array,
});

// Group messages by date
const groupedMessages = computed(() => {
  return props.messages.reduce((acc, message) => {
    const date = formatDate(message.creation, 'ddd, MMM D, YYYY'); // Format as "Mon, Jul 1, 2024"
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(message);
    return acc;
  }, {});
});

const formatDate = (dateString) => {
      if (!dateString) return "";
      const lastInteraction = new Date(dateString);
      let formattedTime = "";
      const currentYear = new Date().getFullYear();
      const messageYear = lastInteraction.getFullYear();

      if (isToday(lastInteraction)) {
        formattedTime =  "Today";
      } else if (isYesterday(lastInteraction)) {
        formattedTime = "Yesterday";
      } else if (currentYear === messageYear) {
        formattedTime = format(lastInteraction, "dd MMM");
      } else {
        formattedTime = format(lastInteraction, "dd/MM/yy");
      }
      return formattedTime;
    };

function formatWhatsAppMessage(message) {
  message = message.replace(/\*(.*?)\*/g, '<b>$1</b>'); // Bold
  message = message.replace(/_(.*?)_/g, '<i>$1</i>'); // Italic
  message = message.replace(/~(.*?)~/g, '<s>$1</s>'); // Strikethrough
  message = message.replace(/\n/g, '<br>'); // New line
  return message;
}
</script>
