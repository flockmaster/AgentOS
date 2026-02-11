/* Main JavaScript - Scroll Engine (T-005) */
(function initBrandingSite() {
  const sections = document.querySelectorAll("section[id]");
  const anchorLinks = document.querySelectorAll('a[href^="#"]');
  const typewriterTarget = document.getElementById("typewriter-text");
  const terminalLog = document.getElementById("terminal-log");
  const heroSection = document.getElementById("hero");
  const reduceMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const revealConfigs = [
    { selector: "#hero .hero-content", effect: "fade-up" },
    { selector: "#visual-terminal .terminal-window", effect: "slide-in-right" },
    { selector: "#bento-grid .bento-card", effect: "fade-up" },
  ];

  revealConfigs.forEach(({ selector, effect }) => {
    document.querySelectorAll(selector).forEach((element, index) => {
      element.classList.add("scroll-reveal");
      if (selector === "#bento-grid .bento-card") {
        element.classList.add(index % 2 === 0 ? "slide-in-left" : "slide-in-right");
        return;
      }
      element.classList.add(effect);
    });
  });

  const revealElements = document.querySelectorAll(".scroll-reveal");

  if (sections.length > 0 || revealElements.length > 0) {
    const observer = new IntersectionObserver(
      (entries, activeObserver) => {
        entries.forEach((entry) => {
          const target = entry.target;

          if (target.matches("section[id]")) {
            const id = target.id;
            const isActive = entry.isIntersecting && entry.intersectionRatio > 0.5;

            if (isActive) {
              target.classList.add("active");
              console.log(`Section ${id} active`);
            } else {
              target.classList.remove("active");
            }
          }

          if (target.classList.contains("scroll-reveal")) {
            const isVisible = entry.isIntersecting && entry.intersectionRatio >= 0.1;

            if (isVisible) {
              target.classList.add("is-visible");
              activeObserver.unobserve(target);
            }
          }
        });
      },
      {
        threshold: [0, 0.1, 0.5, 1],
      },
    );

    sections.forEach((section) => observer.observe(section));
    revealElements.forEach((element) => observer.observe(element));
  }

  if (heroSection && !reduceMotion) {
    let ticking = false;

    const applyParallax = () => {
      const offset = Math.min(window.scrollY * 0.2, 120);
      heroSection.style.setProperty("--hero-parallax", `${offset}px`);
      ticking = false;
    };

    const onScroll = () => {
      if (ticking) {
        return;
      }

      ticking = true;
      window.requestAnimationFrame(applyParallax);
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    applyParallax();
  }

  anchorLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      const href = link.getAttribute("href") || "";
      const targetId = href.slice(1);
      const target = document.getElementById(targetId);

      if (!target) {
        return;
      }

      event.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
      history.pushState(null, "", href);
    });
  });

  if (typewriterTarget && terminalLog) {
    const startupCommand = "/start --mode evolution";
    const startupLogs = [
      "Memory context loaded",
      "Skill matrix initialized",
      "Workflow gates validated",
      "Execution ready",
    ];

    if (reduceMotion) {
      typewriterTarget.textContent = startupCommand;
      startupLogs.forEach((line) => {
        const item = document.createElement("li");
        item.textContent = line;
        item.classList.add("is-visible");
        terminalLog.appendChild(item);
      });
      return;
    }

    let charIndex = 0;
    const typewriterTimer = window.setInterval(() => {
      if (charIndex >= startupCommand.length) {
        window.clearInterval(typewriterTimer);
        startupLogs.forEach((line, index) => {
          window.setTimeout(() => {
            const item = document.createElement("li");
            item.textContent = line;
            terminalLog.appendChild(item);
            window.requestAnimationFrame(() => item.classList.add("is-visible"));
          }, 300 * (index + 1));
        });
        return;
      }

      typewriterTarget.textContent += startupCommand.charAt(charIndex);
      charIndex += 1;
    }, 65);
  }
})();
