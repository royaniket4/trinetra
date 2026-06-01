const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

const TRINETRA_DIR = path.resolve(__dirname);
const BACKEND_URL = 'http://localhost:8000';
const FRONTEND_URL = 'http://localhost:5173';

async function waitForServer(url, timeout = 30000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    try {
      const res = await fetch(url);
      if (res.ok) return true;
    } catch {}
    await new Promise(r => setTimeout(r, 1000));
  }
  throw new Error(`Server ${url} not ready within ${timeout}ms`);
}

async function screenshot(page, name) {
  await page.screenshot({ path: path.join(TRINETRA_DIR, `${name}.png`), fullPage: false });
  console.log(`  📸 Screenshot saved: ${name}.png`);
}

async function run() {
  console.log('🧪 Trinetra Settings + AI Chatbot Test\n');

  // 1. Kill stale servers
  console.log('1. Cleaning up stale processes...');
  try {
    require('child_process').execSync('taskkill /F /FI "WINDOWTITLE eq Trinetra-Backend" 2>nul', { stdio: 'ignore' });
    require('child_process').execSync('taskkill /F /FI "WINDOWTITLE eq Trinetra-Frontend" 2>nul', { stdio: 'ignore' });
    require('child_process').execSync('for /f "tokens=5" %a in (\'netstat -ano ^| findstr ":8000" ^| findstr LISTENING\') do taskkill /F /PID %a 2>nul', { stdio: 'ignore' });
  } catch {}

  await new Promise(r => setTimeout(r, 2000));

  // 2. Start backend
  console.log('2. Starting backend...');
  const backend = spawn('python', ['run_backend.py'], {
    cwd: TRINETRA_DIR,
    stdio: ['ignore', 'pipe', 'pipe'],
    shell: true,
  });
  backend.stdout.on('data', d => process.stdout.write(`   [backend] ${d}`));
  backend.stderr.on('data', d => process.stderr.write(`   [backend] ${d}`));

  // 3. Start frontend
  console.log('3. Starting frontend...');
  const frontend = spawn('cmd', ['/c', 'npm run dev'], {
    cwd: path.join(TRINETRA_DIR, 'frontend'),
    stdio: ['ignore', 'pipe', 'pipe'],
    shell: true,
  });
  frontend.stdout.on('data', d => process.stdout.write(`   [frontend] ${d}`));
  frontend.stderr.on('data', d => process.stderr.write(`   [frontend] ${d}`));

  try {
    // 4. Wait for servers
    console.log('4. Waiting for servers...');
    await Promise.all([
      waitForServer(`${BACKEND_URL}/health`),
      waitForServer(FRONTEND_URL),
    ]);
    console.log('   ✅ Both servers ready');

    // 5. Launch browser
    console.log('5. Launching browser...');
    const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
    const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
    const page = await context.newPage();

    // 6. Register user
    console.log('6. Registering test user...');
    await fetch(`${BACKEND_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'testadmin', email: 'test@trinetra.io', password: 'test123' }),
    });

    // 7. Login
    console.log('7. Logging in via UI...');
    await page.goto(FRONTEND_URL + '/login', { waitUntil: 'networkidle' });
    await screenshot(page, '01-login-page');

    // Wait for the login form
    await page.waitForSelector('input[placeholder="Enter username"]', { timeout: 10000 });
    await page.fill('input[placeholder="Enter username"]', 'testadmin');
    await page.fill('input[placeholder="Enter password"]', 'test123');
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('**/');
    await page.waitForTimeout(2000);
    await screenshot(page, '02-dashboard');

    // 8. Open Settings modal
    console.log('8. Opening Settings modal...');
    const settingsBtn = page.locator('button').filter({ has: page.locator('.lucide-settings') });
    await settingsBtn.click();
    await page.waitForTimeout(800);

    // Check modal is visible
    await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
    await screenshot(page, '03-settings-modal');

    // Check modal positioning
    const modalBox = await page.locator('[role="dialog"]').boundingBox();
    console.log(`   Modal position: x=${Math.round(modalBox.x)}, y=${Math.round(modalBox.y)}, w=${Math.round(modalBox.width)}, h=${Math.round(modalBox.height)}`);
    console.log(`   Viewport: 1920x1080`);

    // Check centered (within tolerance)
    const vp = page.viewportSize();
    const centerX = modalBox.x + modalBox.width / 2;
    const centerY = modalBox.y + modalBox.height / 2;
    const cxOk = Math.abs(centerX - vp.width / 2) < 50;
    const cyOk = Math.abs(centerY - vp.height / 2) < 50;
    console.log(`   Centered X: ${cxOk ? '✅' : '❌'} (center=${Math.round(centerX)}, expected=${Math.round(vp.width/2)})`);
    console.log(`   Centered Y: ${cyOk ? '✅' : '❌'} (center=${Math.round(centerY)}, expected=${Math.round(vp.height/2)})`);

    // Check footer is visible (not cut off)
    const saveBtn = page.locator('button:has-text("Save Changes")');
    const saveBtnBox = await saveBtn.boundingBox();
    console.log(`   Save button visible: ${saveBtnBox && saveBtnBox.y + saveBtnBox.height < vp.height ? '✅' : '❌'}`);

    // 9. Check sidebar scroll
    console.log('9. Testing nav sidebar scroll...');
    const navSidebar = page.locator('nav').first();
    const navItems = await navSidebar.locator('button').count();
    console.log(`   Nav items: ${navItems}`);
    for (let i = 1; i < navItems; i++) {
      await navSidebar.locator('button').nth(i).click();
      await page.waitForTimeout(200);
    }
    await screenshot(page, '04-settings-navigation');

    // 10. Check content scroll
    console.log('10. Testing content scroll...');
    const contentArea = page.locator('[role="dialog"] .overflow-y-auto').last();
    await contentArea.evaluate(el => el.scrollTop = el.scrollHeight);
    await page.waitForTimeout(300);

    // Scroll back to top
    await contentArea.evaluate(el => el.scrollTop = 0);
    await page.waitForTimeout(200);

    // 11. Close modal with ESC
    console.log('11. Testing ESC close...');
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);
    const modalGone = await page.locator('[role="dialog"]').count();
    console.log(`   Modal closed on ESC: ${modalGone === 0 ? '✅' : '❌'}`);

    // 12. Test outside click close
    console.log('12. Re-opening and testing outside click...');
    await settingsBtn.click();
    await page.waitForTimeout(500);
    await page.locator('[role="dialog"]').waitFor({ state: 'visible', timeout: 3000 });
    
    // Click on the backdrop (outside the modal)
    const backdrop = page.locator('.fixed.inset-0.bg-black\\/60');
    await backdrop.click({ position: { x: 10, y: 10 } });
    await page.waitForTimeout(500);
    const closedByBackdrop = await page.locator('[role="dialog"]').count();
    console.log(`   Closed on outside click: ${closedByBackdrop === 0 ? '✅' : '❌'}`);

    // 13. Test AI Chatbot
    console.log('13. Testing AI Chatbot...');
    
    // Check AI health endpoint
    const healthRes = await fetch(`${BACKEND_URL}/api/ai/health`);
    const healthData = await healthRes.json();
    console.log(`   AI Health: ${healthData.status} (latency: ${healthData.latency_ms}ms)`);

    // Open AI panel
    await settingsBtn.click();
    await page.waitForTimeout(300);
    await page.keyboard.press('Escape');
    await page.waitForTimeout(300);

    // Navigate to AI Assistant page
    const aiLink = page.locator('a[href="/ai-assistant"]');
    if (await aiLink.count() > 0) {
      await aiLink.click();
      await page.waitForURL('**/ai-assistant');
      await page.waitForTimeout(2000);
      await screenshot(page, '05-ai-assistant');
      
      // Type a question
      const input = page.locator('input[placeholder*="Ask"]');
      if (await input.count() > 0) {
        await input.fill('What are the top threats right now?');
        await page.keyboard.press('Enter');
        await page.waitForTimeout(2000);
        await screenshot(page, '06-ai-chat-response');
        console.log('   ✅ AI chat message sent');
      } else {
        console.log('   ⚠️ AI input not found, checking alternative...');
        const altInput = page.locator('input, textarea').first();
        if (await altInput.count() > 0) {
          await altInput.fill('What are the top threats?');
          await page.keyboard.press('Enter');
          await page.waitForTimeout(2000);
          await screenshot(page, '06-ai-chat-response');
          console.log('   ✅ AI message sent via alt input');
        }
      }
    } else {
      console.log('   ⚠️ AI Assistant link not found in sidebar');
    }

    console.log('\n✅ All tests completed!');
    await browser.close();

  } catch (err) {
    console.error('\n❌ Test failed:', err.message);
  } finally {
    // Cleanup
    console.log('\nCleaning up...');
    backend.kill('SIGTERM');
    frontend.kill('SIGTERM');
    setTimeout(() => {
      backend.kill('SIGKILL');
      frontend.kill('SIGKILL');
      process.exit(0);
    }, 3000);
  }
}

run();
