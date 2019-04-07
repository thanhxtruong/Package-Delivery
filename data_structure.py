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


# BSTNode class
class BSTNode:
    def __init__(self, data, parent, left=None, right=None):
        self.data = data
        self.left = left
        self.right = right
        self.parent = parent

    def count(self):
        leftCount = 0
        rightCount = 0
        if self.left is not None:
            leftCount = self.left.count()
        if self.right is not None:
            rightCount = self.right.count()
        return 1 + leftCount + rightCount

    def get_successor(self):
        # Successor resides in right subtree, if present
        if self.right is not None:
            successor = self.right
            while successor.left is not None:
                successor = successor.left
            return successor

        # Otherwise the successor is up the tree
        # Traverse up the tree until a parent is encountered from the left
        node = self
        while node.parent is not None and node == node.parent.right:
            node = node.parent
        return node.parent

    def replace_child(self, current_child, new_child):
        if current_child is self.left:
            self.left = new_child
            if self.left:
                self.left.parent = self
        elif current_child is self.right:
            self.right = new_child
            if self.right:
                self.right.parent = self


class BSTIterator:
    def __init__(self, node):
        self.node = node

    def __next__(self):  # For Python versions >= 3
        return self.next()

    def next(self):  # For Python versions < 3
        if self.node is None:
            raise StopIteration
        else:
            current = self.node.data
            self.node = self.node.get_successor()
            return current


# Set class, implemented using a BST
class Set:
    def __init__(self, get_key_function=None):
        self.storage_root = None
        if get_key_function is None:
            # By default, the key of an element is itself
            self.get_key = lambda el: el
        else:
            self.get_key = get_key_function

    def __iter__(self):
        if self.storage_root is None:
            return BSTIterator(None)
        minNode = self.storage_root
        while minNode.left is not None:
            minNode = minNode.left
        return BSTIterator(minNode)

    def add(self, new_element):
        new_elementKey = self.get_key(new_element)
        if self.node_search(new_elementKey) is not None:
            return False

        newNode = BSTNode(new_element, None)
        if self.storage_root is None:
            self.storage_root = newNode
        else:
            node = self.storage_root
            while node is not None:
                if new_elementKey < self.get_key(node.data):
                    # Go left
                    if node.left:
                        node = node.left
                    else:
                        node.left = newNode
                        newNode.parent = node
                        return True
                else:
                    # Go right
                    if node.right:
                        node = node.right
                    else:
                        node.right = newNode
                        newNode.parent = node
                        return True

    def difference(self, other_set):
        result = Set(self.get_key)
        for element in self:
            if other_set.search(self.get_key(element)) is None:
                result.add(element)
        return result

    def filter(self, predicate):
        result = Set(self.get_key)
        for element in self:
            if predicate(element):
                result.add(element)
        return result

    def intersection(self, other_set):
        result = Set(self.get_key)
        for element in self:
            if other_set.search(self.get_key(element)) is not None:
                result.add(element)
        return result

    def __len__(self):
        if self.storage_root is None:
            return 0
        return self.storage_root.count()

    def map(self, map_function):
        result = Set(self.get_key)
        for element in self:
            new_element = map_function(element)
            result.add(new_element)
        return result

    def node_search(self, key):
        # Search the BST
        node = self.storage_root
        while node is not None:
            # Get the node's key
            node_key = self.get_key(node.data)

            # Compare against the search key
            if node_key == key:
                return node
            elif key > node_key:
                node = node.right
            else:
                node = node.left
        return node

    def remove(self, key):
        self.remove_node(self.node_search(key))

    def remove_node(self, node_to_remove):
        if node_to_remove is not None:
            # Case 1: Internal node with 2 children
            if node_to_remove.left is not None and node_to_remove.right is not None:
                successor = node_to_remove.get_successor()

                # Copy the data value from the successor
                dataCopy = successor.data

                # Remove successor
                self.remove_node(successor)

                # Replace node_to_remove's data with successor data
                node_to_remove.data = dataCopy

            # Case 2: Root node (with 1 or 0 children)
            elif node_to_remove is self.storage_root:
                if node_to_remove.left is not None:
                    self.storage_root = node_to_remove.left
                else:
                    self.storage_root = node_to_remove.right

                if self.storage_root:
                    self.storage_root.parent = None

            # Case 3: Internal node with left child only
            elif node_to_remove.left is not None:
                node_to_remove.parent.replace_child(node_to_remove, node_to_remove.left)

            # Case 4: Internal node with right child only, or leaf node
            else:
                node_to_remove.parent.replace_child(node_to_remove, node_to_remove.right)

    def search(self, key):
        # Search the BST
        node = self.node_search(key)
        if node is not None:
            return node.data
        return None

    def union(self, other_set):
        result = Set(self.get_key)
        for element in self:
            result.add(element)
        for element in other_set:
            result.add(element)
        return result

    def show_set(self):
        for element in self:
            print(element, end=" ")
        print("")
