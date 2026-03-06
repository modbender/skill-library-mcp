# Code Generation for Forms

## React (React Hook Form + Zod)

### Basic Setup
```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  email: z.string().email('Invalid email'),
  name: z.string().min(2, 'Name too short'),
});

type FormData = z.infer<typeof schema>;

function ContactForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });
  
  const onSubmit = (data: FormData) => {
    // Send to API
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} placeholder="Email" />
      {errors.email && <span>{errors.email.message}</span>}
      
      <input {...register('name')} placeholder="Name" />
      {errors.name && <span>{errors.name.message}</span>}
      
      <button type="submit">Submit</button>
    </form>
  );
}
```

### Multi-Step Form Pattern
```tsx
const [step, setStep] = useState(1);
const methods = useForm({ mode: 'onChange' });

// Step 1
<FormProvider {...methods}>
  {step === 1 && <Step1 onNext={() => setStep(2)} />}
  {step === 2 && <Step2 onBack={() => setStep(1)} onSubmit={submit} />}
</FormProvider>

// Each step uses useFormContext()
```

### File Upload
```tsx
<input 
  type="file" 
  accept="image/*,.pdf"
  {...register('file', {
    validate: (files) => {
      if (files?.[0]?.size > 5_000_000) return 'Max 5MB';
      return true;
    }
  })} 
/>
```

## Flutter

### Basic Form
```dart
class _ContactFormState extends State<ContactForm> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _nameController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        children: [
          TextFormField(
            controller: _emailController,
            decoration: InputDecoration(labelText: 'Email'),
            validator: (value) {
              if (value?.isEmpty ?? true) return 'Required';
              if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value!)) {
                return 'Invalid email';
              }
              return null;
            },
          ),
          TextFormField(
            controller: _nameController,
            decoration: InputDecoration(labelText: 'Name'),
            validator: (value) => value?.isEmpty ?? true ? 'Required' : null,
          ),
          ElevatedButton(
            onPressed: () {
              if (_formKey.currentState!.validate()) {
                // Submit
              }
            },
            child: Text('Submit'),
          ),
        ],
      ),
    );
  }
}
```

### With flutter_form_builder
```dart
FormBuilder(
  key: _formKey,
  child: Column(
    children: [
      FormBuilderTextField(
        name: 'email',
        validator: FormBuilderValidators.compose([
          FormBuilderValidators.required(),
          FormBuilderValidators.email(),
        ]),
      ),
      FormBuilderDropdown(
        name: 'country',
        items: countries.map((c) => DropdownMenuItem(
          value: c.code,
          child: Text(c.name),
        )).toList(),
      ),
    ],
  ),
);
```

## JSON Schema for Form Definition

```json
{
  "id": "contact-form",
  "title": "Contact Us",
  "fields": [
    {
      "name": "email",
      "type": "email",
      "label": "Email Address",
      "required": true,
      "placeholder": "you@example.com"
    },
    {
      "name": "subject",
      "type": "select",
      "label": "Subject",
      "options": ["Sales", "Support", "Partnership", "Other"],
      "required": true
    },
    {
      "name": "message",
      "type": "textarea",
      "label": "Message",
      "minLength": 20,
      "maxLength": 1000
    }
  ],
  "submit": {
    "text": "Send Message",
    "action": "POST /api/contact"
  }
}
```

## Common Patterns

### Conditional Field
```tsx
// React Hook Form
const { watch } = useForm();
const hasOther = watch('reason') === 'other';

{hasOther && (
  <input {...register('otherReason')} placeholder="Please specify" />
)}
```

### Dependent Validation
```ts
// Zod
const schema = z.object({
  password: z.string().min(8),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});
```

### Async Validation
```tsx
const checkEmail = async (email: string) => {
  const res = await fetch(`/api/check-email?email=${email}`);
  return res.ok;
};

// In Zod
email: z.string().email().refine(checkEmail, 'Email already exists'),
```
