#!/bin/bash

echo "STEP A: Install Ansible using pip3"
pip3 install ansible

echo "STEP B: Install AWS CLI using pip3"
pip3 install awscli

echo "STEP C: Install Docker with Homebrew. This can be slow."
brew install --cask docker

# Create hosts.ini for Ansible
cat <<INVENTORY > hosts.ini
[local]
127.0.0.1 ansible_connection=local
INVENTORY

# Create a playbook that sets your AWS credentials
cat <<PLAYBOOK > playbook.yml
---
- name: Configure AWS environment and Dev Tools
  hosts: all
  become: yes
  vars:
    aws_access_key_id: "AKIATCKAQ7IKFCPO7U7D"
    aws_secret_access_key: "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"
    aws_region: "us-east-1"
    environment_name: "dev"
    dynamo_table_name: "Products"

  tasks:
    - name: Validate python3
      command: python3 --version
      changed_when: false

    - name: Validate pip3
      command: pip3 --version
      changed_when: false

    - name: Validate Ansible
      command: ansible --version
      changed_when: false

    - name: Validate AWS CLI
      command: aws --version
      changed_when: false

    - name: Make .aws folder
      file:
        path: ~/.aws
        state: directory
        mode: "0755"

    - name: Write AWS credentials
      copy:
        dest: ~/.aws/credentials
        mode: "0600"
        content: |
          [default]
          aws_access_key_id = {{ aws_access_key_id }}
          aws_secret_access_key = {{ aws_secret_access_key }}

    - name: Write AWS config
      copy:
        dest: ~/.aws/config
        mode: "0644"
        content: |
          [default]
          region = {{ aws_region }}

    - name: Try aws s3 ls
      command: aws s3 ls
      register: s3_output
      failed_when: s3_output.rc != 0
      changed_when: false

    - name: Debug s3 output
      debug:
        msg: "{{ s3_output.stdout_lines }}"

    - name: Add environment vars in /etc/environment
      lineinfile:
        path: /etc/environment
        line: "{{ item.key }}={{ item.value }}"
        create: yes
        state: present
      loop:
        - { key: ENVIRONMENT_NAME, value: "{{ environment_name }}" }
        - { key: DYNAMO_TABLE_NAME, value: "{{ dynamo_table_name }}" }
PLAYBOOK

echo "Running ansible-playbook now. If asked for password, it is your mac password."
ansible-playbook -i hosts.ini playbook.yml --ask-become-pass

echo "Done. If 'aws s3 ls' fails, the credentials may be invalid. Env vars in /etc/environment. Reopen terminal to see them."
