# Node class
class Node:
    def __init__(self, address):
        self.data = address
        self.next = None


# LinkedList data structure
class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def append(self, new_node):
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

    def prepend(self, new_node):
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node

    def insert_after(self, current_node, new_node):
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        elif current_node is self.tail:
            self.tail.next = new_node
            self.tail = new_node
        else:
            new_node.next = current_node.next
            current_node.next = new_node

    def remove_after(self, current_node):
        # Special case, remove head
        if (current_node is None) and (self.head is not None):
            succeeding_node = self.head.next
            self.head = succeeding_node
            if succeeding_node is None:  # Removed last item
                self.tail = None
        elif current_node.next is not None:
            succeeding_node = current_node.next.next
            current_node.next = succeeding_node
            if succeeding_node is None:  # Removed tail
                self.tail = current_node


# Queue data structure
class Queue:
    def __init__(self):
        self.list = LinkedList()

    # Insert as list tail (end of queue)
    def push(self, new_item):
        self.list.append(new_item)

    def pop(self):
        # Copy list head (front of queue)
        popped_item = self.list.head
        # Remove list head
        self.list.remove_after(None)
        # Return popped item
        return popped_item
