from awsx import AWSOTP

if __name__ == "__main__":
    otp = AWSOTP("+94763453736").send()
    print(otp)
