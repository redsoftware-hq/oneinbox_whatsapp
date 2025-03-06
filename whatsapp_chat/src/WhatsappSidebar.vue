<template>
  <div class="h-4/5 w-100 bg-white  flex flex-col border-r border-gray-100 ">
    <div class="p-4 flex justify-between items-center border-b  bg-gray-100 bg-white">
      
      <h2 class="text-lg font-semibold text-gray-700">Contacts</h2>
    </div>

    <div class="p-2">
      <input
        v-model="search"
        type="text"
        placeholder="Search contacts..."
        class="w-full p-2 rounded-md border border-gray-300 focus:outline-none focus:ring focus:ring-blue-300 bg-gray-100"
      />
    </div>

    <div class="flex-1 overflow-y-auto bg-white">
      <ul v-if="filteredContacts.length">
        <li
          v-for="contact in filteredContacts"
          :key="contact.phone"
          class="flex items-center justify-between p-4 cursor-pointer transition-duration-200 hover:bg-gray-100 border-b border-gray-300 bg-white w-full"
          :class="{ 'bg-blue-100': selectedContact === contact.phone }"
          @click="selectContact(contact)"
        >
          <div class="flex flex-col space-y-2 w-full">
            <div class="flex justify-between w-full">
              <div class="text-lg font-medium text-gray-800">{{ contact.phone }}</div>
              <Badge
                v-if="contact.unread_message_count > 0"
                variant="solid"
                theme="green"
                size="sm"
              >
                {{ contact.unread_message_count }}
              </Badge>
            </div>

            <div class="flex justify-between w-full">
              <div class="text-sm text-gray-800">{{ contact.whatsapp_name || "" }}</div>
              <div class="text-sm font-medium text-gray-400">{{ formatDate(contact.last_message_time) || "" }}</div>
            </div>
          </div>
        </li>
      </ul>

      <div v-else-if="contacts.loading" class="text-gray-500 text-center p-4">Loading contacts...</div>
      <div v-else class="text-gray-500 text-center p-4">No contacts found</div>
    </div>
  </div>
</template>

<script>
import { Badge, createResource } from "frappe-ui";
import { format, isToday, isYesterday } from "date-fns";



export default {
  name: "WhatsappSidebar",
  data() {
    return {
      search: "",
      selectedContact: null,
    };
  },
  setup() {
    const contacts = createResource({
      url: "/api/method/frappe_whatsapp.api.whatsapp.get_whatsapp_contact",
      auto: true,
    });

    return { contacts };
  },
  computed: {
    filteredContacts() {
      return (this.contacts.data || []).filter(
        (contact) =>
          contact.phone.toLowerCase().includes(this.search.toLowerCase()) ||
          (contact.whatsapp_name || "").toLowerCase().includes(this.search.toLowerCase())
      );
    },
  },
  methods: {
    selectContact(contact) {
      this.selectedContact = contact.phone;
      this.$emit("contact-selected", { number: contact.phone, name: contact.whatsapp_name });
    },
    formatDate(dateString) {
      const lastInteraction = new Date(dateString);
      let formattedTime=""
      const currentYear = new Date().getFullYear();
      const messageYear = lastInteraction.getFullYear();

if (isToday(lastInteraction)) {
    formattedTime = format(lastInteraction, "hh:mm a");
  } else if (isYesterday(lastInteraction)) {
    formattedTime = "Yesterday";
  } else if (currentYear === messageYear) {
    formattedTime = format(lastInteraction, "dd MMM");
  } else {
    formattedTime = format(lastInteraction, "dd/MM/yy");
  }
  return formattedTime
    },
  },
};
</script>

<style scoped>
/* Custom scrollbar */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 10px;
}

/* Smooth transitions */
li {
  transition: background-color 0.2s ease-in-out;
}
</style>
