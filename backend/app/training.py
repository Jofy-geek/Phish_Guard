from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np

# Define the Dataset class
class PhishingDataset(Dataset):
    def _init_(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def _len_(self):
        return len(self.texts)

    def _getitem_(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]

        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            return_attention_mask=True,
            return_tensors='pt',
            truncation=True
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

# Load dataset
data = {
    'text': [
        # Phishing (label=1)
        "Hello, this is Officer Kim from the Seoul Police Department. We have detected suspicious transactions linked to your bank account. Please verify your identity to assist in the investigation.",
        "This is a final notice from the Financial Crimes Unit. We need to confirm your ID to process the fraud report on your account.",
        "Hi, I'm calling from your bank's security team. We've seen unusual activity on your account. Could you please verify your account number and PIN to secure it?",
        "Good afternoon. I'm Investigator Lee from the Seoul District Prosecutor's Office. Your information was found in a case under investigation. Could you confirm your details to clear this up?",
        "Hello, this is the Customer Security Department. We have flagged unauthorized access to your account. To resolve this, please confirm your bank account information over the phone.",
        "I'm calling from the Fraud Department at your bank. There was an attempt to transfer funds from your account. We need your account details to freeze the transfer.",
        "This is Officer Choi from the National Tax Service. Your financial records show irregularities. Please confirm your identity number for verification.",
        "Hello, I'm contacting you from the Central Bank's Fraud Division. We need to confirm some recent transactions linked to your ID. Could you share your account number?",
        "This is an urgent call from the Security Division. We need your cooperation in securing your funds due to suspected fraud. Could you confirm your date of birth and bank details?",
        "I'm Agent Park from the Anti-Fraud Task Force. We've flagged your account for potential fraud. Please verify your credit card details for security purposes.",
        "This is the Customer Protection Agency. A transaction was flagged as suspicious on your account. To secure it, please confirm your account number.",
        "Hi, I'm calling from the Bank of Korea. Your account has been flagged for suspicious transactions. We need your banking details to verify your identity.",
        "This is the Seoul Prosecutor's Office. We suspect illegal activity linked to your name. To proceed, please provide your ID and phone number.",
        "Hello, I'm from your bank's Fraud Prevention team. We've detected an attempted withdrawal. Could you verify your account number to prevent the transaction?",
        "This is Officer Han from the Financial Security Department. We have reports of unauthorized access to your financial information. Please confirm your ID to protect your funds.",
        "I'm from the Cyber Security Team. There was a breach attempt on your account. For verification, could you share your bank details and address?",
        "This is Investigator Yoon from the Seoul Financial Crimes Unit. We need to confirm your recent transactions to clear you from a suspected fraud case.",
        "Hello, this is your bank's Fraud Department. We need to confirm recent activity. Could you please share your account number and identity number?",
        "This is Officer Lim from the Financial Investigation Bureau. We've detected suspicious account activity and need to confirm your ID to secure your funds.",
        "I'm calling from the Seoul Tax Bureau. We detected irregularities in your tax records linked to your account. Please confirm your personal information over the phone.",
        "This is the Customer Fraud Alert Division. We have a possible security issue on your account. Please verify your date of birth and bank details to proceed.",
        "Hi, this is the Anti-Phishing Unit. Your phone number has been linked to suspicious activity. Please confirm your ID and account number to resolve this.",
        "This is the Seoul Financial Authority. We've detected suspicious loan applications in your name. To confirm your identity, please share your ID number.",
        "Hello, this is the Identity Verification Division. To protect your funds from an attempted fraud, please confirm your personal details.",
        "I'm from the Seoul District Attorney's office. Your account was used in a fraud case. Please verify your personal information to clear your name.",
        "This is a security alert from your bank. There was an attempted withdrawal from your account. Please verify your account details to secure it.",
        "Hello, I'm from the National Tax Investigation Department. We've detected a tax issue linked to your ID. Please confirm your identity to proceed.",
        "This is a courtesy call from the Financial Protection Unit. We need to verify recent transactions on your account. Please confirm your account number.",
        "This is Officer Shin from the Cybercrime Unit. Your account was flagged for suspicious activity. Please verify your bank information for security.",
        "Hello, I'm from the Seoul Government's Financial Compliance Team. To complete a security check, please confirm your personal ID and account details.",
        "This is the Customer Security Division. We detected a large transfer attempt. To secure your account, please provide your account number.",
        "Hello, this is the Banking Oversight Authority. We have a potential fraud case linked to your account. Could you confirm your ID?",
        "This is Officer Jang from the National Financial Security Bureau. Your account shows unauthorized activity. Please confirm your details over the phone.",
        "Hello, I'm from your bank's Customer Support. We've noticed a failed login attempt. To secure your account, please confirm your account and ID number.",
        "This is a security call from the Fraud Detection Department. Please confirm your recent transactions to avoid account suspension.",
        "Good afternoon. I'm with the Financial Security Task Force. We need to verify your identity to prevent fraud.",
        "This is the Seoul Public Prosecutor's Office. Your ID was used in a fraud attempt. Please confirm your details to clear this issue.",
        "Hello, this is the Anti-Phishing Division. We have flagged suspicious activity linked to your phone number. Please confirm your ID and address.",
        "I'm calling from your bank's security team. There was an attempt to transfer funds from your account. Could you provide your banking details to verify?",
        "This is Officer Lee from the National Tax Office. We need to verify your records to complete a security audit.",
        
        # Non-phishing (label=0)
        "HELLO", "HI", 
        "Hi, this is Dr. Kim's office reminding you of your appointment tomorrow at 10 AM. Please let us know if you need to reschedule.",
        "Hello! Just a friendly reminder to bring your ID for your scheduled vaccine appointment this Friday.",
        "Hi, this is Lee from the bookstore. Your reserved book has arrived and is ready for pick-up.",
        "Hello! This is your gym calling to let you know that your membership renewal is due next month.",
        "Hey, it's Park from the community center. We're holding a lost-and-found event this weekend if you'd like to check for your items.",
        "Hello, this is Kim from the flower shop. Your arrangement is ready for pick-up.",
        "Hi, this is an automated message from your utility provider. Your bill is due in 3 days.",
        "This is a reminder from your dentist's office to bring your insurance card to your appointment on Thursday.",
        "Hello, this is the library. Just a reminder that your borrowed books are due back next week.",
        "Hi, this is Park's pet clinic. We're reminding you of your pet's grooming appointment this Saturday.",
        "Hello, this is your car service center. Your scheduled maintenance is coming up next week.",
        "This is a reminder from the pharmacy that your prescription is ready for pick-up.",
        "Hello, this is the vet. Your pet's vaccinations are due soon. Contact us to schedule an appointment.",
        "Hi, this is Kim from the bank. Just reminding you of your account review meeting tomorrow at 2 PM.",
        "Hello, this is your local community center. We're hosting a health seminar this Friday. Join us if interested!",
        "Hello! This is a reminder from your insurance provider. Your renewal is due next month.",
        "Hi, this is a courtesy call from your gym. Just reminding you of the new classes starting this month.",
        "Hello, this is the neighborhood association. We have a meeting scheduled for this Wednesday at 7 PM.",
        "Hello, this is the bakery. Just letting you know your special order is ready for pick-up.",
        "Hi, this is Park from the clinic. You're due for a follow-up. Please give us a call to schedule.",
        "Hello, this is the auto shop. Your vehicle service has been completed and is ready for pick-up.",
        "Hi, this is Kim from your bank's customer service. Just checking in to remind you of your appointment with us.",
        "Hello! This is a reminder from the library. You have books due back next Monday.",
        "Hi, this is the clinic. Just a reminder to fast before your lab test tomorrow.",
        "Hello, this is your subscription service. We wanted to confirm your delivery details for next week's package.",
        "Hi, this is your utility company. This is a courtesy call reminding you to update your payment method.",
        "Hello, this is the wellness center. We're confirming your spa appointment on Friday.",
        "This is the apartment management office. We're notifying you of maintenance work scheduled for this weekend.",
        "Hello, this is Kim from the pharmacy. Your prescription is ready for pick-up.",
        "Hi, this is the school office. We're calling to remind you of the parent-teacher meeting next Tuesday.",
        "Hello, this is the dental clinic. Just confirming your cleaning appointment for next Thursday.",
        "Hi, this is the vet clinic. It's time for your pet's annual check-up. Please give us a call to schedule.",
        "Hello, this is Kim from the community center. We're confirming your registration for the cooking class.",
        "Hi, this is your car service center. Your scheduled oil change is coming up on Saturday.",
        "Hello, this is Park from the bank. We're reminding you of the annual account update. No action needed.",
        "Hi, this is the hospital. Just confirming your MRI appointment on Friday.",
        "Hello, this is the library. Just a reminder that your borrowed items are due soon.",
        "Hi, this is Kim from the bank. We wanted to confirm your scheduled appointment for account review.",
        "Hello, this is the pet groomer. Just a reminder for your pet's grooming session on Wednesday.",
        "Hello! This is your doctor's office calling to confirm your upcoming check-up.",

        #Phishing Part2
        "You've won a free iPhone!", 
        "Your account has been compromised.",
        "Please confirm your password.",
        "Meeting at 10 AM tomorrow.",
        "I'm from the Seoul Central District Prosecutor's Office and need to verify some information.",
        "Your loan of 30 million won has been processed. Please confirm.",
        "Hello, you have a pending transaction for 4 million won. Contact us to avoid penalties.",
        "Kids on Facebook seem a bit different. I thought Facebook was uncool back then, but now Instagram seems cool.",
        "That's why there aren't many companies. Small companies often lack the funds for marketing, but demand is high in certain sectors.",
        "If you have a lower GPA, it doesn't mean you didn't work hard. People can still appreciate the effort you put in."
    ],
    
    'label' : [
        # Phishing labels
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        # Non-phishing labels
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,

        #phishing part2
        1, 1, 1, 0, 1, 1, 1, 0, 0, 0,
        

    ]
}


texts = data['text']
labels = data['label']

# Split the dataset into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(texts, labels, test_size=0.2, random_state=42)

# Initialize tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
tokenizer.save_pretrained('C:/Users/Jofy/Desktop/FinalProject/phishing_detection_model')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

# Create datasets
train_dataset = PhishingDataset(X_train, y_train, tokenizer, max_len=128)
val_dataset = PhishingDataset(X_val, y_val, tokenizer, max_len=128)

# Set training arguments
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    evaluation_strategy="epoch"
)

# Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

# Train the model
trainer.train()

# Save the model
trainer.save_model('./phishing_detection_model')

# Optional: Evaluate the model
trainer.evaluate()
