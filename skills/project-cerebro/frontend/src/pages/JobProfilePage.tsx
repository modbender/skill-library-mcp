import { useState, useEffect } from 'react';
import { User, Save, FileText, Plus, Trash2, Briefcase, GraduationCap } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Toggle } from '../components/ui/Toggle';

interface WorkExperience {
  id: string;
  jobTitle: string;
  company: string;
  location: string;
  startDate: string;
  endDate: string;
  currentJob: boolean;
  responsibilities: string;
}

interface Education {
  id: string;
  institution: string;
  degree: string;
  fieldOfStudy: string;
  location: string;
  startDate: string;
  endDate: string;
  graduated: boolean;
  expectedGraduation: string;
  gpa: string;
}

interface JobProfile {
  profile: {
    personal: {
      full_name: string;
      email: string;
      phone: string;
      location: {
        address: string;
        city: string;
        state: string;
        country: string;
        zip_code: string;
      };
      linkedin_url: string;
      portfolio_url: string;
      github_url: string;
    };
    work_authorization: {
      authorized_to_work_us: boolean;
      requires_visa_sponsorship: boolean;
      willing_to_relocate: boolean;
      open_to_remote: boolean;
    };
    veteran_status: {
      is_veteran: boolean;
      is_protected_veteran: boolean;
      disability_status: 'yes' | 'no' | 'prefer_not_to_say';
    };
    job_type_preference: {
      looking_for: 'full-time' | 'internship' | 'both';
      preferred_start_date: string;
      available_immediately: boolean;
    };
    work_experience: WorkExperience[];
    education: Education[];
    skills: {
      programming_languages: string[];
      frameworks: string[];
      tools: string[];
      soft_skills: string[];
      certifications: string[];
      languages: string[];
    };
    preferences: {
      hourly_rate: {
        minimum: number;
        preferred: number;
        currency: string;
      };
      industries_of_interest: string[];
      deal_breakers: string[];
      company_size_preference: string[];
    };
    documents: {
      resume_path: string;
    };
    screening_answers: {
      why_looking: string;
      greatest_strength: string;
      greatest_weakness: string;
      why_this_company: string;
      salary_expectations_text: string;
      availability: string;
    };
  };
  search_criteria: {
    job_titles: string[];
    keywords_required: string[];
    keywords_preferred: string[];
    keywords_excluded: string[];
    experience_levels: string[];
    company_blacklist: string[];
  };
}

function generateId() {
  return Math.random().toString(36).substring(2, 9);
}

export function JobProfilePage() {
  const [profile, setProfile] = useState<JobProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  // Store raw input values for array fields to allow free typing
  const [arrayInputs, setArrayInputs] = useState<Record<string, string>>({});

  useEffect(() => {
    fetch('/api/job-profile')
      .then((r) => r.json())
      .then((data) => {
        // Migrate old profile format to new format
        const loaded = data.profile || getDefaultProfile();
        const migrated = migrateProfile(loaded);
        setProfile(migrated);
        setLoading(false);
      })
      .catch(() => {
        setProfile(getDefaultProfile());
        setLoading(false);
      });
  }, []);

  const handleSave = async () => {
    if (!profile) return;
    setSaving(true);
    try {
      await fetch('/api/job-profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile }),
      });
      setLastSaved(new Date());
    } catch (e) {
      console.error('Failed to save profile:', e);
    } finally {
      setSaving(false);
    }
  };

  const updateProfile = (path: string, value: any) => {
    if (!profile) return;
    const newProfile = JSON.parse(JSON.stringify(profile));
    const parts = path.split('.');
    let cur: any = newProfile;
    for (let i = 0; i < parts.length - 1; i++) {
      if (!cur[parts[i]]) cur[parts[i]] = {};
      cur = cur[parts[i]];
    }
    cur[parts[parts.length - 1]] = value;
    setProfile(newProfile);
  };

  // Handle array field input - store raw value for display, update array on blur
  const handleArrayInputChange = (inputKey: string, value: string) => {
    setArrayInputs((prev) => ({ ...prev, [inputKey]: value }));
  };

  const handleArrayInputBlur = (inputKey: string, profilePath: string) => {
    const rawValue = arrayInputs[inputKey] ?? '';
    const arr = rawValue.split(',').map((s) => s.trim()).filter(Boolean);
    updateProfile(profilePath, arr);
    // Normalize display value
    setArrayInputs((prev) => ({ ...prev, [inputKey]: arr.join(', ') }));
  };

  // Work Experience helpers
  const addWorkExperience = () => {
    if (!profile) return;
    const newExp: WorkExperience = {
      id: generateId(),
      jobTitle: '',
      company: '',
      location: '',
      startDate: '',
      endDate: '',
      currentJob: false,
      responsibilities: '',
    };
    updateProfile('profile.work_experience', [...(profile.profile.work_experience || []), newExp]);
  };

  const updateWorkExperience = (id: string, field: keyof WorkExperience, value: any) => {
    setProfile((prev) => {
      if (!prev) return prev;
      const workExp = prev.profile.work_experience || [];
      const updated = workExp.map((exp) =>
        exp.id === id ? { ...exp, [field]: value } : exp
      );
      return {
        ...prev,
        profile: {
          ...prev.profile,
          work_experience: updated,
        },
      };
    });
  };

  const removeWorkExperience = (id: string) => {
    if (!profile) return;
    const updated = (profile.profile.work_experience || []).filter((exp) => exp.id !== id);
    updateProfile('profile.work_experience', updated);
  };

  // Education helpers
  const addEducation = () => {
    if (!profile) return;
    const newEdu: Education = {
      id: generateId(),
      institution: '',
      degree: '',
      fieldOfStudy: '',
      location: '',
      startDate: '',
      endDate: '',
      graduated: false,
      expectedGraduation: '',
      gpa: '',
    };
    updateProfile('profile.education', [...(profile.profile.education || []), newEdu]);
  };

  const updateEducation = (id: string, field: keyof Education, value: any) => {
    setProfile((prev) => {
      if (!prev) return prev;
      const education = prev.profile.education || [];
      const updated = education.map((edu) =>
        edu.id === id ? { ...edu, [field]: value } : edu
      );
      return {
        ...prev,
        profile: {
          ...prev.profile,
          education: updated,
        },
      };
    });
  };

  const removeEducation = (id: string) => {
    if (!profile) return;
    const updated = (profile.profile.education || []).filter((edu) => edu.id !== id);
    updateProfile('profile.education', updated);
  };

  if (loading || !profile) {
    return <div className="p-8 text-center text-muted-foreground">Loading...</div>;
  }

  return (
    <div className="p-8 space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
            <User className="w-8 h-8 text-blue-400" />
            Job Profile
          </h1>
          <p className="text-muted-foreground">
            Master application template — used by the Job Application Brain
          </p>
        </div>
        <div className="flex items-center gap-3">
          {lastSaved && (
            <span className="text-xs text-muted-foreground">
              Saved {lastSaved.toLocaleTimeString()}
            </span>
          )}
          <Button variant="primary" onClick={handleSave} disabled={saving}>
            <Save className="w-4 h-4 mr-2" />
            {saving ? 'Saving...' : 'Save Profile'}
          </Button>
        </div>
      </header>

      {/* Personal Info */}
      <Card>
        <h2 className="text-lg font-semibold mb-4">Personal Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <label className="text-sm font-medium">Full Name *</label>
            <Input
              value={profile.profile.personal.full_name}
              onChange={(e) => updateProfile('profile.personal.full_name', e.target.value)}
              placeholder="John Doe"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Email *</label>
            <Input
              type="email"
              value={profile.profile.personal.email}
              onChange={(e) => updateProfile('profile.personal.email', e.target.value)}
              placeholder="john@example.com"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Phone *</label>
            <Input
              value={profile.profile.personal.phone}
              onChange={(e) => updateProfile('profile.personal.phone', e.target.value)}
              placeholder="+1-555-123-4567"
            />
          </div>
          <div className="md:col-span-2">
            <label className="text-sm font-medium">Street Address</label>
            <Input
              value={profile.profile.personal.location.address || ''}
              onChange={(e) => updateProfile('profile.personal.location.address', e.target.value)}
              placeholder="123 Main St, Apt 4"
            />
          </div>
          <div>
            <label className="text-sm font-medium">City *</label>
            <Input
              value={profile.profile.personal.location.city}
              onChange={(e) => updateProfile('profile.personal.location.city', e.target.value)}
              placeholder="San Francisco"
            />
          </div>
          <div>
            <label className="text-sm font-medium">State *</label>
            <Input
              value={profile.profile.personal.location.state}
              onChange={(e) => updateProfile('profile.personal.location.state', e.target.value)}
              placeholder="CA"
            />
          </div>
          <div>
            <label className="text-sm font-medium">ZIP Code</label>
            <Input
              value={profile.profile.personal.location.zip_code}
              onChange={(e) => updateProfile('profile.personal.location.zip_code', e.target.value)}
              placeholder="94102"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Country</label>
            <Input
              value={profile.profile.personal.location.country}
              onChange={(e) => updateProfile('profile.personal.location.country', e.target.value)}
              placeholder="USA"
            />
          </div>
          <div>
            <label className="text-sm font-medium">LinkedIn URL</label>
            <Input
              value={profile.profile.personal.linkedin_url}
              onChange={(e) => updateProfile('profile.personal.linkedin_url', e.target.value)}
              placeholder="https://linkedin.com/in/..."
            />
          </div>
          <div>
            <label className="text-sm font-medium">GitHub URL</label>
            <Input
              value={profile.profile.personal.github_url}
              onChange={(e) => updateProfile('profile.personal.github_url', e.target.value)}
              placeholder="https://github.com/..."
            />
          </div>
          <div className="md:col-span-2">
            <label className="text-sm font-medium">Portfolio/Website URL</label>
            <Input
              value={profile.profile.personal.portfolio_url}
              onChange={(e) => updateProfile('profile.personal.portfolio_url', e.target.value)}
              placeholder="https://..."
            />
          </div>
        </div>
      </Card>

      {/* Job Type Preference */}
      <Card>
        <h2 className="text-lg font-semibold mb-4">Job Type Preference</h2>
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">Looking For *</label>
            <select
              value={profile.profile.job_type_preference?.looking_for || 'full-time'}
              onChange={(e) => updateProfile('profile.job_type_preference.looking_for', e.target.value)}
              className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary"
            >
              <option value="full-time">Full-Time Employment</option>
              <option value="internship">Internship</option>
              <option value="both">Both (Full-Time or Internship)</option>
            </select>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">Preferred Start Date</label>
              <Input
                type="date"
                value={profile.profile.job_type_preference?.preferred_start_date || ''}
                onChange={(e) => updateProfile('profile.job_type_preference.preferred_start_date', e.target.value)}
              />
            </div>
            <div className="flex items-center justify-between p-4 bg-secondary/30 rounded-lg">
              <div>
                <div className="font-medium">Available Immediately</div>
              </div>
              <Toggle
                checked={profile.profile.job_type_preference?.available_immediately || false}
                onChange={(v) => updateProfile('profile.job_type_preference.available_immediately', v)}
              />
            </div>
          </div>
        </div>
      </Card>

      {/* Work Experience */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-blue-400" />
            Work Experience
          </h2>
          <Button variant="secondary" size="sm" onClick={addWorkExperience}>
            <Plus className="w-4 h-4 mr-1" />
            Add Experience
          </Button>
        </div>
        
        {(profile.profile.work_experience || []).length === 0 ? (
          <div className="text-center py-8 text-muted-foreground border-2 border-dashed border-border rounded-lg">
            <Briefcase className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>No work experience added yet</p>
            <Button variant="secondary" size="sm" className="mt-2" onClick={addWorkExperience}>
              <Plus className="w-4 h-4 mr-1" />
              Add Your First Job
            </Button>
          </div>
        ) : (
          <div className="space-y-6">
            {(profile.profile.work_experience || []).map((exp, index) => (
              <div key={exp.id} className="p-4 border border-border rounded-lg bg-secondary/20">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-medium text-muted-foreground">Experience #{index + 1}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeWorkExperience(exp.id)}
                    className="text-red-400 hover:text-red-300"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Job Title *</label>
                    <Input
                      value={exp.jobTitle}
                      onChange={(e) => updateWorkExperience(exp.id, 'jobTitle', e.target.value)}
                      placeholder="Software Engineer"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Company *</label>
                    <Input
                      value={exp.company}
                      onChange={(e) => updateWorkExperience(exp.id, 'company', e.target.value)}
                      placeholder="Acme Corp"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Location</label>
                    <Input
                      value={exp.location}
                      onChange={(e) => updateWorkExperience(exp.id, 'location', e.target.value)}
                      placeholder="San Francisco, CA"
                    />
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <label className="text-sm font-medium">Start Date *</label>
                      <Input
                        type="month"
                        value={exp.startDate}
                        onChange={(e) => updateWorkExperience(exp.id, 'startDate', e.target.value)}
                      />
                    </div>
                    <div className="flex-1">
                      <label className="text-sm font-medium">End Date</label>
                      <Input
                        type="month"
                        value={exp.currentJob ? '' : exp.endDate}
                        onChange={(e) => updateWorkExperience(exp.id, 'endDate', e.target.value)}
                        disabled={!!exp.currentJob}
                        className={exp.currentJob ? 'opacity-50 cursor-not-allowed' : ''}
                      />
                      {exp.currentJob && (
                        <span className="text-xs text-muted-foreground">Present</span>
                      )}
                    </div>
                  </div>
                  <div className="md:col-span-2 flex items-center gap-2">
                    <Toggle
                      checked={!!exp.currentJob}
                      onChange={(v) => {
                        updateWorkExperience(exp.id, 'currentJob', v);
                        if (v) updateWorkExperience(exp.id, 'endDate', '');
                      }}
                    />
                    <span 
                      className="text-sm cursor-pointer select-none"
                      onClick={() => {
                        const newVal = !exp.currentJob;
                        updateWorkExperience(exp.id, 'currentJob', newVal);
                        if (newVal) updateWorkExperience(exp.id, 'endDate', '');
                      }}
                    >
                      I currently work here
                    </span>
                  </div>
                  <div className="md:col-span-2">
                    <label className="text-sm font-medium">Responsibilities & Achievements</label>
                    <textarea
                      value={exp.responsibilities}
                      onChange={(e) => updateWorkExperience(exp.id, 'responsibilities', e.target.value)}
                      placeholder="• Led development of...\n• Increased efficiency by...\n• Collaborated with..."
                      className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary min-h-[120px]"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Education */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <GraduationCap className="w-5 h-5 text-green-400" />
            Education
          </h2>
          <Button variant="secondary" size="sm" onClick={addEducation}>
            <Plus className="w-4 h-4 mr-1" />
            Add Education
          </Button>
        </div>
        
        {(profile.profile.education || []).length === 0 ? (
          <div className="text-center py-8 text-muted-foreground border-2 border-dashed border-border rounded-lg">
            <GraduationCap className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>No education added yet</p>
            <Button variant="secondary" size="sm" className="mt-2" onClick={addEducation}>
              <Plus className="w-4 h-4 mr-1" />
              Add Education
            </Button>
          </div>
        ) : (
          <div className="space-y-6">
            {(profile.profile.education || []).map((edu, index) => (
              <div key={edu.id} className="p-4 border border-border rounded-lg bg-secondary/20">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-medium text-muted-foreground">Education #{index + 1}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeEducation(edu.id)}
                    className="text-red-400 hover:text-red-300"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="md:col-span-2">
                    <label className="text-sm font-medium">Institution *</label>
                    <Input
                      value={edu.institution}
                      onChange={(e) => updateEducation(edu.id, 'institution', e.target.value)}
                      placeholder="University of California, Berkeley"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Degree *</label>
                    <select
                      value={edu.degree}
                      onChange={(e) => updateEducation(edu.id, 'degree', e.target.value)}
                      className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary"
                    >
                      <option value="">Select degree...</option>
                      <option value="High School Diploma">High School Diploma</option>
                      <option value="Associate's">Associate's Degree</option>
                      <option value="Bachelor's">Bachelor's Degree</option>
                      <option value="Master's">Master's Degree</option>
                      <option value="PhD">PhD / Doctorate</option>
                      <option value="Certificate">Certificate</option>
                      <option value="Bootcamp">Bootcamp</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Field of Study *</label>
                    <Input
                      value={edu.fieldOfStudy}
                      onChange={(e) => updateEducation(edu.id, 'fieldOfStudy', e.target.value)}
                      placeholder="Computer Science"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Location</label>
                    <Input
                      value={edu.location}
                      onChange={(e) => updateEducation(edu.id, 'location', e.target.value)}
                      placeholder="Berkeley, CA"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">GPA (optional)</label>
                    <Input
                      value={edu.gpa}
                      onChange={(e) => updateEducation(edu.id, 'gpa', e.target.value)}
                      placeholder="3.8 / 4.0"
                    />
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <label className="text-sm font-medium">Start Date</label>
                      <Input
                        type="month"
                        value={edu.startDate}
                        onChange={(e) => updateEducation(edu.id, 'startDate', e.target.value)}
                      />
                    </div>
                    <div className="flex-1">
                      <label className="text-sm font-medium">End Date</label>
                      <Input
                        type="month"
                        value={edu.endDate}
                        onChange={(e) => updateEducation(edu.id, 'endDate', e.target.value)}
                        disabled={!edu.graduated}
                      />
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Toggle
                      checked={edu.graduated}
                      onChange={(v) => updateEducation(edu.id, 'graduated', v)}
                    />
                    <span className="text-sm">Already graduated</span>
                  </div>
                  {!edu.graduated && (
                    <div>
                      <label className="text-sm font-medium">Expected Graduation</label>
                      <Input
                        type="month"
                        value={edu.expectedGraduation}
                        onChange={(e) => updateEducation(edu.id, 'expectedGraduation', e.target.value)}
                      />
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Work Authorization */}
      <Card>
        <h2 className="text-lg font-semibold mb-4">Work Authorization</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-secondary/30 rounded-lg">
            <div>
              <div className="font-medium">Authorized to work in the US</div>
              <div className="text-xs text-muted-foreground">Without employer sponsorship</div>
            </div>
            <Toggle
              checked={profile.profile.work_authorization.authorized_to_work_us}
              onChange={(v) => updateProfile('profile.work_authorization.authorized_to_work_us', v)}
            />
          </div>
          <div className="flex items-center justify-between p-4 bg-secondary/30 rounded-lg">
            <div>
              <div className="font-medium">Will require visa sponsorship</div>
              <div className="text-xs text-muted-foreground">Now or in the future</div>
            </div>
            <Toggle
              checked={profile.profile.work_authorization.requires_visa_sponsorship}
              onChange={(v) => updateProfile('profile.work_authorization.requires_visa_sponsorship', v)}
            />
          </div>
          <div className="flex items-center justify-between p-4 bg-secondary/30 rounded-lg">
            <div>
              <div className="font-medium">Willing to relocate</div>
            </div>
            <Toggle
              checked={profile.profile.work_authorization.willing_to_relocate}
              onChange={(v) => updateProfile('profile.work_authorization.willing_to_relocate', v)}
            />
          </div>
          <div className="flex items-center justify-between p-4 bg-secondary/30 rounded-lg">
            <div>
              <div className="font-medium">Open to remote work</div>
            </div>
            <Toggle
              checked={profile.profile.work_authorization.open_to_remote}
              onChange={(v) => updateProfile('profile.work_authorization.open_to_remote', v)}
            />
          </div>
        </div>
      </Card>

      {/* Veteran Status */}
      <Card>
        <h2 className="text-lg font-semibold mb-4">Veteran Status</h2>
        <p className="text-sm text-muted-foreground mb-4">
          This information is for equal opportunity compliance. It will not affect your candidacy.
        </p>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-secondary/30 rounded-lg">
            <div>
              <div className="font-medium">I am a veteran</div>
              <div className="text-xs text-muted-foreground">Have served in the U.S. Armed Forces</div>
            </div>
            <Toggle
              checked={profile.profile.veteran_status?.is_veteran || false}
              onChange={(v) => updateProfile('profile.veteran_status.is_veteran', v)}
            />
          </div>
          {profile.profile.veteran_status?.is_veteran && (
            <div className="flex items-center justify-between p-4 bg-secondary/30 rounded-lg">
              <div>
                <div className="font-medium">Protected veteran</div>
                <div className="text-xs text-muted-foreground">
                  Disabled veteran, recently separated, active duty wartime, or campaign badge veteran
                </div>
              </div>
              <Toggle
                checked={profile.profile.veteran_status?.is_protected_veteran || false}
                onChange={(v) => updateProfile('profile.veteran_status.is_protected_veteran', v)}
              />
            </div>
          )}
          <div>
            <label className="text-sm font-medium">Disability Status</label>
            <select
              value={profile.profile.veteran_status?.disability_status || 'prefer_not_to_say'}
              onChange={(e) => updateProfile('profile.veteran_status.disability_status', e.target.value)}
              className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary"
            >
              <option value="prefer_not_to_say">I don't wish to answer</option>
              <option value="no">No, I don't have a disability</option>
              <option value="yes">Yes, I have a disability (or previously had one)</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Skills */}
      <Card>
        <h2 className="text-lg font-semibold mb-4">Skills & Qualifications</h2>
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">Programming Languages (comma-separated)</label>
            <Input
              value={arrayInputs['skills.programming_languages'] ?? (profile.profile.skills?.programming_languages || []).join(', ')}
              onChange={(e) => handleArrayInputChange('skills.programming_languages', e.target.value)}
              onBlur={() => handleArrayInputBlur('skills.programming_languages', 'profile.skills.programming_languages')}
              placeholder="Python, JavaScript, Go, TypeScript"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Frameworks & Libraries (comma-separated)</label>
            <Input
              value={arrayInputs['skills.frameworks'] ?? (profile.profile.skills?.frameworks || []).join(', ')}
              onChange={(e) => handleArrayInputChange('skills.frameworks', e.target.value)}
              onBlur={() => handleArrayInputBlur('skills.frameworks', 'profile.skills.frameworks')}
              placeholder="React, Django, Node.js, FastAPI"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Tools & Technologies (comma-separated)</label>
            <Input
              value={arrayInputs['skills.tools'] ?? (profile.profile.skills?.tools || []).join(', ')}
              onChange={(e) => handleArrayInputChange('skills.tools', e.target.value)}
              onBlur={() => handleArrayInputBlur('skills.tools', 'profile.skills.tools')}
              placeholder="Docker, AWS, Git, Kubernetes"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Certifications (comma-separated)</label>
            <Input
              value={arrayInputs['skills.certifications'] ?? (profile.profile.skills?.certifications || []).join(', ')}
              onChange={(e) => handleArrayInputChange('skills.certifications', e.target.value)}
              onBlur={() => handleArrayInputBlur('skills.certifications', 'profile.skills.certifications')}
              placeholder="AWS Solutions Architect, PMP"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Languages Spoken (comma-separated)</label>
            <Input
              value={arrayInputs['skills.languages'] ?? (profile.profile.skills?.languages || []).join(', ')}
              onChange={(e) => handleArrayInputChange('skills.languages', e.target.value)}
              onBlur={() => handleArrayInputBlur('skills.languages', 'profile.skills.languages')}
              placeholder="English (Native), Spanish (Conversational)"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Soft Skills (comma-separated)</label>
            <Input
              value={arrayInputs['skills.soft_skills'] ?? (profile.profile.skills?.soft_skills || []).join(', ')}
              onChange={(e) => handleArrayInputChange('skills.soft_skills', e.target.value)}
              onBlur={() => handleArrayInputBlur('skills.soft_skills', 'profile.skills.soft_skills')}
              placeholder="Leadership, Communication, Problem Solving"
            />
          </div>
        </div>
      </Card>

      {/* Preferences */}
      <Card>
        <h2 className="text-lg font-semibold mb-4">Preferences</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium">Minimum Hourly Rate ($)</label>
            <Input
              type="number"
              value={profile.profile.preferences?.hourly_rate?.minimum || ''}
              onChange={(e) => updateProfile('profile.preferences.hourly_rate.minimum', parseInt(e.target.value) || 0)}
              placeholder="50"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Preferred Hourly Rate ($)</label>
            <Input
              type="number"
              value={profile.profile.preferences?.hourly_rate?.preferred || ''}
              onChange={(e) => updateProfile('profile.preferences.hourly_rate.preferred', parseInt(e.target.value) || 0)}
              placeholder="75"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Currency</label>
            <select
              value={profile.profile.preferences?.hourly_rate?.currency || 'USD'}
              onChange={(e) => updateProfile('profile.preferences.hourly_rate.currency', e.target.value)}
              className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary"
            >
              <option value="USD">USD ($)</option>
              <option value="EUR">EUR (€)</option>
              <option value="GBP">GBP (£)</option>
              <option value="CAD">CAD (C$)</option>
              <option value="AUD">AUD (A$)</option>
            </select>
          </div>
          <div>
            <label className="text-sm font-medium">Industries of Interest (comma-separated)</label>
            <Input
              value={arrayInputs['prefs.industries'] ?? (profile.profile.preferences?.industries_of_interest || []).join(', ')}
              onChange={(e) => handleArrayInputChange('prefs.industries', e.target.value)}
              onBlur={() => handleArrayInputBlur('prefs.industries', 'profile.preferences.industries_of_interest')}
              placeholder="Tech, Fintech, Healthcare"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Company Size Preference (comma-separated)</label>
            <Input
              value={arrayInputs['prefs.companySize'] ?? (profile.profile.preferences?.company_size_preference || []).join(', ')}
              onChange={(e) => handleArrayInputChange('prefs.companySize', e.target.value)}
              onBlur={() => handleArrayInputBlur('prefs.companySize', 'profile.preferences.company_size_preference')}
              placeholder="Startup, Mid-size, Enterprise"
            />
          </div>
          <div className="md:col-span-2">
            <label className="text-sm font-medium">Deal Breakers (comma-separated)</label>
            <Input
              value={arrayInputs['prefs.dealbreakers'] ?? (profile.profile.preferences?.deal_breakers || []).join(', ')}
              onChange={(e) => handleArrayInputChange('prefs.dealbreakers', e.target.value)}
              onBlur={() => handleArrayInputBlur('prefs.dealbreakers', 'profile.preferences.deal_breakers')}
              placeholder="No remote option, On-call 24/7, Less than 2 weeks PTO"
            />
          </div>
        </div>
      </Card>

      {/* Screening Answers */}
      <Card>
        <h2 className="text-lg font-semibold mb-4">Common Screening Questions</h2>
        <p className="text-sm text-muted-foreground mb-4">
          Pre-fill answers to common application questions. The Job Brain will use these when filling out applications.
        </p>
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">Why are you looking for a new position?</label>
            <textarea
              value={profile.profile.screening_answers?.why_looking || ''}
              onChange={(e) => updateProfile('profile.screening_answers.why_looking', e.target.value)}
              placeholder="I'm seeking new challenges and growth opportunities..."
              className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary min-h-[80px]"
            />
          </div>
          <div>
            <label className="text-sm font-medium">What is your greatest strength?</label>
            <textarea
              value={profile.profile.screening_answers?.greatest_strength || ''}
              onChange={(e) => updateProfile('profile.screening_answers.greatest_strength', e.target.value)}
              placeholder="My ability to..."
              className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary min-h-[80px]"
            />
          </div>
          <div>
            <label className="text-sm font-medium">What is a weakness you're working on?</label>
            <textarea
              value={profile.profile.screening_answers?.greatest_weakness || ''}
              onChange={(e) => updateProfile('profile.screening_answers.greatest_weakness', e.target.value)}
              placeholder="I sometimes..."
              className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary min-h-[80px]"
            />
          </div>
          <div>
            <label className="text-sm font-medium">What interests you about this company? (template)</label>
            <textarea
              value={profile.profile.screening_answers?.why_this_company || ''}
              onChange={(e) => updateProfile('profile.screening_answers.why_this_company', e.target.value)}
              placeholder="I'm drawn to companies with strong engineering culture and..."
              className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary min-h-[80px]"
            />
          </div>
          <div>
            <label className="text-sm font-medium">What are your salary expectations?</label>
            <Input
              value={profile.profile.screening_answers?.salary_expectations_text || ''}
              onChange={(e) => updateProfile('profile.screening_answers.salary_expectations_text', e.target.value)}
              placeholder="Market rate based on experience and location"
            />
          </div>
          <div>
            <label className="text-sm font-medium">When are you available to start / interview?</label>
            <Input
              value={profile.profile.screening_answers?.availability || ''}
              onChange={(e) => updateProfile('profile.screening_answers.availability', e.target.value)}
              placeholder="2 weeks notice / Flexible schedule for interviews"
            />
          </div>
        </div>
      </Card>

      {/* Search Criteria */}
      <Card>
        <h2 className="text-lg font-semibold mb-4">Job Search Criteria</h2>
        <p className="text-sm text-muted-foreground mb-4">
          These settings guide the Job Brain when searching for positions.
        </p>
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">Job Titles to Search (comma-separated)</label>
            <Input
              value={arrayInputs['search.job_titles'] ?? profile.search_criteria.job_titles.join(', ')}
              onChange={(e) => handleArrayInputChange('search.job_titles', e.target.value)}
              onBlur={() => handleArrayInputBlur('search.job_titles', 'search_criteria.job_titles')}
              placeholder="Software Engineer, Backend Developer, Full Stack Engineer"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Required Keywords (comma-separated)</label>
            <Input
              value={arrayInputs['search.keywords_required'] ?? profile.search_criteria.keywords_required.join(', ')}
              onChange={(e) => handleArrayInputChange('search.keywords_required', e.target.value)}
              onBlur={() => handleArrayInputBlur('search.keywords_required', 'search_criteria.keywords_required')}
              placeholder="python, api"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Preferred Keywords (comma-separated)</label>
            <Input
              value={arrayInputs['search.keywords_preferred'] ?? profile.search_criteria.keywords_preferred.join(', ')}
              onChange={(e) => handleArrayInputChange('search.keywords_preferred', e.target.value)}
              onBlur={() => handleArrayInputBlur('search.keywords_preferred', 'search_criteria.keywords_preferred')}
              placeholder="aws, kubernetes, machine learning"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Excluded Keywords (comma-separated)</label>
            <Input
              value={arrayInputs['search.keywords_excluded'] ?? profile.search_criteria.keywords_excluded.join(', ')}
              onChange={(e) => handleArrayInputChange('search.keywords_excluded', e.target.value)}
              onBlur={() => handleArrayInputBlur('search.keywords_excluded', 'search_criteria.keywords_excluded')}
              placeholder="java, frontend-only, unpaid"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Experience Levels (comma-separated)</label>
            <Input
              value={arrayInputs['search.experience_levels'] ?? profile.search_criteria.experience_levels.join(', ')}
              onChange={(e) => handleArrayInputChange('search.experience_levels', e.target.value)}
              onBlur={() => handleArrayInputBlur('search.experience_levels', 'search_criteria.experience_levels')}
              placeholder="entry-level, mid-level, senior"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Company Blacklist (comma-separated)</label>
            <Input
              value={arrayInputs['search.company_blacklist'] ?? profile.search_criteria.company_blacklist.join(', ')}
              onChange={(e) => handleArrayInputChange('search.company_blacklist', e.target.value)}
              onBlur={() => handleArrayInputBlur('search.company_blacklist', 'search_criteria.company_blacklist')}
              placeholder="Companies you don't want to apply to"
            />
          </div>
        </div>
      </Card>

      {/* Documents */}
      <Card>
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <FileText className="w-5 h-5" />
          Documents
        </h2>
        <div>
          <label className="text-sm font-medium">Resume Path</label>
          <Input
            value={profile.profile.documents.resume_path}
            onChange={(e) => updateProfile('profile.documents.resume_path', e.target.value)}
            placeholder="~/Documents/resume.pdf"
          />
          <p className="text-xs text-muted-foreground mt-1">
            Path to your resume file on the server. This will be used for all applications.
          </p>
        </div>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end pb-8">
        <Button variant="primary" size="lg" onClick={handleSave} disabled={saving}>
          <Save className="w-5 h-5 mr-2" />
          {saving ? 'Saving...' : 'Save Profile'}
        </Button>
      </div>
    </div>
  );
}

function migrateProfile(old: any): JobProfile {
  const defaults = getDefaultProfile();
  
  // Deep merge with defaults
  const profile = {
    profile: {
      personal: { ...defaults.profile.personal, ...old.profile?.personal },
      work_authorization: { ...defaults.profile.work_authorization, ...old.profile?.work_authorization },
      veteran_status: { ...defaults.profile.veteran_status, ...old.profile?.veteran_status },
      job_type_preference: { ...defaults.profile.job_type_preference, ...old.profile?.job_type_preference },
      // Ensure arrays
      work_experience: Array.isArray(old.profile?.work_experience) ? old.profile.work_experience : [],
      education: Array.isArray(old.profile?.education) ? old.profile.education : [],
      skills: { ...defaults.profile.skills, ...old.profile?.skills },
      preferences: { 
        ...defaults.profile.preferences, 
        ...old.profile?.preferences,
        hourly_rate: { 
          ...defaults.profile.preferences.hourly_rate, 
          ...old.profile?.preferences?.hourly_rate 
        }
      },
      documents: { ...defaults.profile.documents, ...old.profile?.documents },
      screening_answers: { ...defaults.profile.screening_answers, ...old.profile?.screening_answers },
    },
    search_criteria: { ...defaults.search_criteria, ...old.search_criteria },
  };

  // Migrate old education object format to array format
  if (old.profile?.education && !Array.isArray(old.profile.education)) {
    const oldEdu = old.profile.education;
    if (oldEdu.university || oldEdu.highest_degree || oldEdu.field_of_study) {
      profile.profile.education = [{
        id: generateId(),
        institution: oldEdu.university || '',
        degree: oldEdu.highest_degree || '',
        fieldOfStudy: oldEdu.field_of_study || '',
        location: '',
        startDate: '',
        endDate: '',
        graduated: !!oldEdu.graduation_year && oldEdu.graduation_year <= new Date().getFullYear(),
        expectedGraduation: '',
        gpa: '',
      }];
    }
  }

  // Migrate old experience object format
  if (old.profile?.experience && !Array.isArray(old.profile.work_experience)) {
    const oldExp = old.profile.experience;
    if (oldExp.current_title) {
      profile.profile.work_experience = [{
        id: generateId(),
        jobTitle: oldExp.current_title || '',
        company: '',
        location: '',
        startDate: '',
        endDate: '',
        currentJob: true,
        responsibilities: (oldExp.specializations || []).join(', '),
      }];
    }
  }

  return profile as JobProfile;
}

function getDefaultProfile(): JobProfile {
  return {
    profile: {
      personal: {
        full_name: '',
        email: '',
        phone: '',
        location: { address: '', city: '', state: '', country: 'USA', zip_code: '' },
        linkedin_url: '',
        portfolio_url: '',
        github_url: '',
      },
      work_authorization: {
        authorized_to_work_us: true,
        requires_visa_sponsorship: false,
        willing_to_relocate: false,
        open_to_remote: true,
      },
      veteran_status: {
        is_veteran: false,
        is_protected_veteran: false,
        disability_status: 'prefer_not_to_say',
      },
      job_type_preference: {
        looking_for: 'full-time',
        preferred_start_date: '',
        available_immediately: false,
      },
      work_experience: [],
      education: [],
      skills: {
        programming_languages: [],
        frameworks: [],
        tools: [],
        soft_skills: [],
        certifications: [],
        languages: [],
      },
      preferences: {
        hourly_rate: { minimum: 0, preferred: 0, currency: 'USD' },
        industries_of_interest: [],
        deal_breakers: [],
        company_size_preference: [],
      },
      documents: { resume_path: '' },
      screening_answers: {
        why_looking: '',
        greatest_strength: '',
        greatest_weakness: '',
        why_this_company: '',
        salary_expectations_text: '',
        availability: '',
      },
    },
    search_criteria: {
      job_titles: [],
      keywords_required: [],
      keywords_preferred: [],
      keywords_excluded: [],
      experience_levels: [],
      company_blacklist: [],
    },
  };
}
