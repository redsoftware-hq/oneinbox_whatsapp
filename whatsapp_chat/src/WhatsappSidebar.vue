<template>
  <div class="h-4/5 w-100 bg-white flex flex-col border-r border-gray-100">
    <div class="p-4 flex justify-between items-center border-b bg-gray-100">
      <h2 class="text-lg font-semibold text-gray-700">Contacts</h2>
    </div>

    <div class="p-2 bg-gray-100">
      <input
        v-model="search"
        type="text"
        placeholder="Search contacts..."
        class="w-full p-2 rounded-md border border-gray-300 focus:outline-none focus:ring focus:ring-blue-300"
      />
    </div>

    <div class="flex-1 overflow-y-auto bg-gray-100">
      <ul v-if="filteredContacts?.length">
        <li
          v-for="contact in filteredContacts"
          :key="contact.phone"
          class="flex items-center justify-between p-4 cursor-pointer transition duration-200 hover:bg-gray-100 border-b border-gray-300 bg-white w-full"
          :class="{ 'bg-blue-100': selectedContact === contact.phone }"
          @click="selectContact(contact)"
        >
          <div class="flex flex-col space-y-2 w-full">
            <div class="flex justify-between w-full">
              <div class="text-lg font-medium text-gray-800">{{ contact.phone }}</div>
              <Badge v-if="contact.unread_message_count > 0" variant="solid" theme="green" size="sm">
                {{ contact.unread_message_count }}
              </Badge>
            </div>

            <div class="flex justify-between w-full">
              <div class="text-sm font-medium text-gray-800">{{ contact.whatsapp_name || "Unknown" }}</div>
              <div class="text-sm font-medium text-gray-400">{{ formatDate(contact.last_message_time) }}</div>
            </div>
          </div>
        </li>
      </ul>

      <div v-else class="text-gray-500 text-center p-4">No contacts found</div>
    </div>
  </div>
</template>

<script>
import { Badge, frappeRequest } from "frappe-ui";
import { format, isToday, isYesterday } from "date-fns";
import { emitter } from "./utils/eventBus.js";
import { ref, computed, watch } from "vue";

export default {
  name: "WhatsappSidebar",

  props: {
    user_update: Boolean,
    socket: Object,
    contacts: Array,
  },

  setup(props) {
    const search = ref("");
    const selectedContact = ref(null);

    const resetMessageCount = async (phone) => {
      if (!phone) return;
      try {
        await fetch("/api/method/frappe_whatsapp.api.whatsapp.reset_unread_count", {
          method: "POST",
          headers: { "Content-Type": "application/json" ,
          "X-Frappe-CSRF-Token": window.frappe.csrf_token
          },
          body: JSON.stringify({ phone }),
        });
      } catch (error) {
        console.error("Error resetting message count:", error);
      }
    };

    const filteredContacts = computed(() => {
      if (!search.value) return props.contacts;
      return props.contacts.filter(
        (contact) =>
          contact.phone.includes(search.value) ||
          (contact.whatsapp_name || "").toLowerCase().includes(search.value.toLowerCase())
      );
    });

    const selectContact = (contact) => {
      selectedContact.value = contact.phone;
      resetMessageCount(selectedContact.value);

      emitter.emit("contact-selected", {
        number: contact.phone,
        name: contact.whatsapp_name,
      });
      localStorage.setItem("selectedContact", JSON.stringify(contact));
      emitter.emit("contact-selected-refresh");
    };

    watch(() => props.contacts, (newContacts) => {
      console.log("Contacts updated:", newContacts);
    });

    const formatDate = (dateString) => {
      if (!dateString) return "";
      const lastInteraction = new Date(dateString);
      let formattedTime = "";
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
      return formattedTime;
    };

    return {
      search,
      selectedContact,
      filteredContacts,
      selectContact,
      formatDate,
    };
  },
};
</script>