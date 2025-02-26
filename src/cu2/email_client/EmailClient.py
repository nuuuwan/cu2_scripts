class EmailClient:

    def normalize_phone_num(self, phone_num):
        phone_num = phone_num.replace(" ", "")
        phone_num = phone_num.replace("-", "")
        assert len(phone_num) == 10
        return phone_num[:3] + "-" + phone_num[3:6] + "-" + phone_num[6:]

    def input_phone_num(self):
        raw_phone_num = input("Enter your phone number: ")
        normalized_phone_num = self.normalize_phone_num(raw_phone_num)
        print("Normalized phone number: ", normalized_phone_num)
        return normalized_phone_num

    def input_otp(self):
        return input("Enter the OTP: ")

    def login(self, phone_num, otp):
        print("Logging in...")

    def input_message(self):
        return input("Enter the message: ")

    def send_message(self, message):
        print("Sending message...")

    def logout(self):
        print("Logging out...")

    def run(self):
        phone_num = self.input_phone_num()
        otp = self.input_otp()
        self.login(phone_num, otp)
        message = self.input_message()
        self.send_message(message)
        self.logout()
