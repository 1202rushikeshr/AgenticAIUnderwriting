import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { finalize } from 'rxjs';
import { ApplicationService } from '../../services/application.service';

import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

@Component({
  selector: 'app-application-submit',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
  ],
  templateUrl: './application-submit.component.html',
  styleUrls: ['./application-submit.component.css'],
})
export class ApplicationSubmitComponent {
  isSubmitting = false;
  submittedId: number | null = null;

  productTypes = ['Term Life', 'Whole Life', 'Health', 'Auto'];

  form = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    email: ['', [Validators.email]],
    contact_number: [''],
    age: [null as number | null, [Validators.required, Validators.min(0), Validators.max(120)]],
    income: [null as number | null, [Validators.required, Validators.min(0)]],
    occupation: [''],
    location: [''],
    prior_claims: [0, [Validators.required, Validators.min(0)]],
    smoking_status: ['non-smoker', [Validators.required]],
    product_type: ['Term Life', [Validators.required]],
    coverage_amount: [100000, [Validators.required, Validators.min(1)]],
  });

  constructor(private fb: FormBuilder, private api: ApplicationService, private snack: MatSnackBar) {}

  resetForm() {
    this.submittedId = null;
    this.form.reset({
      name: '',
      email: '',
      contact_number: '',
      age: null,
      income: null,
      occupation: '',
      location: '',
      prior_claims: 0,
      smoking_status: 'non-smoker',
      product_type: 'Term Life',
      coverage_amount: 100000,
    });
  }

  submit() {
    this.submittedId = null;

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.snack.open('Please fix validation errors and try again.', 'OK', { duration: 3500 });
      return;
    }

    const v = this.form.getRawValue();

    const payload = {
      applicant: {
        name: v.name!,
        email: v.email?.trim() ? v.email.trim() : null,
        contact_number: v.contact_number?.trim() ? v.contact_number.trim() : null,
        age: Number(v.age),
        income: Number(v.income),
        occupation: v.occupation?.trim() ? v.occupation.trim() : null,
        location: v.location?.trim() ? v.location.trim() : null,
        prior_claims: Number(v.prior_claims ?? 0),
        smoking_status: v.smoking_status as 'smoker' | 'non-smoker',
      },
      product_type: v.product_type!,
      coverage_amount: Number(v.coverage_amount),
    };

    this.isSubmitting = true;

    this.api.createApplication(payload)
      .pipe(finalize(() => (this.isSubmitting = false)))
      .subscribe({
        next: (res) => {
          this.submittedId = res.id ?? res.application_id ?? null;
          this.snack.open('Application submitted successfully.', 'OK', { duration: 4000 });
        },
        error: (err) => {
          const msg = err?.error?.detail || err?.message || 'Failed to submit application. Please try again.';
          this.snack.open(msg, 'OK', { duration: 5500 });
        },
      });
  }

  currentYear(): number {
    return new Date().getFullYear();
  }
}
